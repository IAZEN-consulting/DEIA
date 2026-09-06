#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["langchain>=1.0", "langchain-openai>=1.0", "python-dotenv>=1.0"]
# ///
"""The same agent as agent.py, built on create_agent instead of a hand-rolled loop.

create_agent still compiles down to a LangGraph graph; it replaces
langgraph.prebuilt.create_react_agent, deprecated in LangGraph 1.0. LangChain 1.x
needs Python 3.10+, which the script block above pins -- without it uv falls back
to the system interpreter and resolves langchain 0.3, where create_agent is absent.

Usage:
    echo 'OPENROUTER_API_KEY=sk-or-...' > .env
    uv run agent_langgraph.py "build a todo list"
"""

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

import skills as skill_lib

load_dotenv()  # reads OPENROUTER_API_KEY from .env if present

MODELS = [
    "minimax/minimax-m3:free",
    # "cohere/north-mini-code:free",
    # "minimax/minimax-m2.7:free",
]
MAX_STEPS = 12

SYSTEM = """You are a front-end coding agent working in a sandboxed directory.

Build what the user asks for using vanilla HTML, CSS and JavaScript. No build
step, no external dependencies, no CDN links. Entry point is always index.html.

Work in small steps: list what exists, write a file, then move on. Call write_file
once per file, with the complete final content. When everything is written, stop
calling tools and reply with a one-paragraph summary of what you built."""


def make_tools(workspace, skills):
    """Tools close over the workspace, so the sandbox root is never model input."""

    def resolve(path):
        root = workspace.resolve()
        target = (root / path).resolve()
        if target != root and root not in target.parents:
            raise ValueError(f"path escapes the workspace: {path}")
        return target

    @tool
    def write_file(path: str, content: str) -> str:
        """Write (or overwrite) a file with the given content."""
        target = resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"wrote {path} ({len(content)} bytes)"

    @tool
    def read_file(path: str) -> str:
        """Read back a file that was already written."""
        target = resolve(path)
        if not target.is_file():
            return f"no such file: {path}"
        return target.read_text(encoding="utf-8")

    @tool
    def list_files() -> str:
        """List the files currently in the workspace."""
        root = workspace.resolve()
        found = sorted(
            p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()
        )
        return "\n".join(found) if found else "(empty)"

    @tool
    def load_skill(name: str) -> str:
        """Read a skill's full instructions before doing work it covers."""
        skill = skills.get(name)
        if skill is None:
            return f"no such skill: {name}. Available: {', '.join(sorted(skills))}"
        return skill["body"]

    return [write_file, read_file, list_files, load_skill]


def build_models(names):
    """One ChatOpenAI per model id, in priority order, tools left unbound.

    create_agent() binds the tools itself, so the bind_tools() call the
    create_react_agent version needed here is gone. max_retries=3 is the openai
    SDK's own retry, which already honours the provider's Retry-After.
    """
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise SystemExit("set OPENROUTER_API_KEY first")

    return [
        ChatOpenAI(
            model=name,
            base_url="https://openrouter.ai/api/v1",
            api_key=key,
            max_retries=3,
            timeout=180.0,
        )
        for name in names
    ]


def run(task, workspace, models):
    workspace.mkdir(parents=True, exist_ok=True)
    skills = skill_lib.discover()
    tools = make_tools(workspace, skills)
    prompt = SYSTEM + skill_lib.catalog(skills)

    # The first model is the agent's; the rest are handed to the fallback
    # middleware, which retries the call on the next one when a model errors.
    # That is what with_fallbacks() chaining did before.
    primary, *spares = build_models(models)
    agent = create_agent(
        primary,
        tools,
        system_prompt=prompt,
        middleware=[ModelFallbackMiddleware(*spares)] if spares else [],
    )

    final = None
    # stream_mode="values" hands back the whole state after each node, so the
    # newest message is the step that just ran.
    for state in agent.stream(
        {"messages": [HumanMessage(content=task)]},
        config={"recursion_limit": MAX_STEPS * 2},
        stream_mode="values",
    ):
        message = state["messages"][-1]
        if isinstance(message, AIMessage) and message.tool_calls:
            for call in message.tool_calls:
                print(f"  -> {call['name']}({', '.join(call['args'])})")
        elif isinstance(message, ToolMessage):
            print(f"     {str(message.content).splitlines()[0][:70]}")
        elif isinstance(message, AIMessage):
            final = message.content

    return final or "(no final answer)"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", help="what to build")
    parser.add_argument("-w", "--workspace", default="workspace_lg", type=Path)
    parser.add_argument(
        "-m", "--model", action="append", help="override model (repeatable)"
    )
    args = parser.parse_args()

    print(f"task: {args.task}\nworkspace: {args.workspace}\n")
    print(run(args.task, args.workspace, args.model or MODELS))


if __name__ == "__main__":
    main()
