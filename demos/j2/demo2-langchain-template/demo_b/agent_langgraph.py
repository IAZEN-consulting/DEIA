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
    echo 'OPENAI_API_KEY=sk-...' > .env   # or use the .env at the repo root
    uv run agent_langgraph.py "build a todo list"
"""

import argparse
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# load_dotenv never overrides an already-set variable, so the first file to
# define OPENAI_API_KEY wins: a .env next to the script, else the project's own
# at the repo root, four levels above this file.
load_dotenv()
load_dotenv(Path(__file__).resolve().parents[4] / ".env")

# nano reads the skill catalogue but not carefully: given two skills that both
# fit a task, it tends to load whichever it saw first rather than the more
# specific one, and the run then looks fine while quietly skipping the point.
MODELS = ["gpt-4.1-mini-2025-04-14"]
# A check_classes failure costs a read_skill_file, a rewrite and a re-check on
# top of the original steps -- 12 ran out mid-fix on a real page.
MAX_STEPS = 18
SKILLS_DIR = Path(__file__).parent / "skills"

SYSTEM = """You are a front-end coding agent working in a sandboxed directory.

Build what the user asks for using HTML, CSS and JavaScript, no build step and no
framework. Entry point is always index.html. Link an external stylesheet or script
only when a skill you loaded gives you that exact URL, then copy it verbatim.

Load every skill in the catalogue before the first line of markup, never after,
whether or not the task looks related to it -- a skill decides how the file
gets written, so reading it late means writing that file twice, and the
catalogue is not a menu you get to skip. Its rules beat your own defaults. When
two skills fit, the more specific wins: a page for a named organisation is its
design system's job, so load that skill and leave the generic one unread. Never
blend the two.

A skill may be an index pointing at files beside its SKILL.md; read those with
read_skill_file, and pass it a directory to see what it holds. Every class name
you write must come from a file you actually read -- not from memory, however
plausible it looks. Trusting your own memory here is the failure these skills
exist to prevent, and check_classes exists to catch it: after write_file on any
page styled by a skill, call check_classes on it before moving on, and fix
whatever it flags. Give each flagged class one real attempt: read the file that
should document it, then correct or drop it. If it still doesn't check out
after that, the skill's own docs don't cover it -- stop guessing at file paths,
leave the class as your own judgment call, and say so in your summary instead
of chasing it further.

Work in small steps: list what exists, load every skill in the catalogue, write
a file, check its classes, then move on. When everything is written and checked,
stop calling tools and reply with a one-paragraph summary of what you built,
including whatever each skill you loaded asked you to report back."""


def discover_skills(directory=SKILLS_DIR):
    skills = {}
    for path in sorted(Path(directory).glob("*/SKILL.md")):
        meta, body = {}, path.read_text(encoding="utf-8").strip()
        lines = body.splitlines()
        if lines and lines[0].strip() == "---":
            key = None
            for index, line in enumerate(lines[1:], start=2):
                if line.strip() == "---":
                    body = "\n".join(lines[index:]).strip()
                    break
                if line.startswith((" ", "\t")) and key:  # continuation of a value
                    meta[key] = f"{meta[key]} {line.strip()}".strip()
                elif ":" in line:
                    key, _, value = line.partition(":")
                    key = key.strip()
                    meta[key] = value.strip()
            else:
                meta = {}  # front matter never closed: treat the file as all body

        # Keyed by folder name, not by the declared "name:" field: a folder name
        # is always short and ASCII, where a declared name can be long, accented
        # or punctuated -- a small model retyping it drops half and silently
        # falls back to another skill.
        skills[path.parent.name] = {
            "description": meta.get("description", ""),
            "body": body,
            "dir": path.parent,
        }

    return skills


def skill_catalog(skills):
    """Render the handles and descriptions appended to the system prompt.

    Bodies stay on disk until load_skill asks for one, so a run that needs no
    skill keeps a small prompt. Empty string when skills/ holds nothing.
    """
    if not skills:
        return ""

    lines = [
        "",
        "",
        "Available skills, listed by the exact handle load_skill and read_skill_file",
        "take. Read the whole list before loading anything, then load the closest",
        "match in full -- do not guess at its content:",
    ]
    lines += [
        f"- {handle}: {skills[handle]['description']}" for handle in sorted(skills)
    ]
    return "\n".join(lines)


def make_tools(workspace, skills):
    """Tools close over the workspace and the skills: no root is ever model input."""

    def resolve(root, path):
        """Join path under root, refusing anything that climbs back out of it."""
        root = root.resolve()
        target = (root / path).resolve()
        if target != root and root not in target.parents:
            raise ValueError(f"path escapes {root.name}: {path}")
        return target

    @tool
    def write_file(path: str, content: str) -> str:
        """Write (or overwrite) a file with the given content."""
        target = resolve(workspace, path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"wrote {path} ({len(content)} bytes)"

    @tool
    def read_file(path: str) -> str:
        """Read back a file that was already written."""
        target = resolve(workspace, path)
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
            return f"no such skill: {name}. Handles: {', '.join(sorted(skills))}"
        return skill["body"]

    @tool
    def read_skill_file(skill: str, path: str) -> str:
        """Read a file a skill links to from its SKILL.md. A directory path
        lists what it holds."""
        entry = skills.get(skill)
        if entry is None:
            return f"no such skill: {skill}. Handles: {', '.join(sorted(skills))}"

        # resolve() returns an absolute path, so root must be absolute too or the
        # relative_to() below raises. A skill's docs may also link relatively to
        # a file outside its own folder (e.g. copied from a site's own layout),
        # hence the caught escape below instead of a raised exception.
        root = entry["dir"].resolve()
        try:
            target = resolve(root, path)
        except ValueError:
            return f"{path} is outside {skill}: paths start at the skill root."
        if target.is_dir():
            found = sorted(
                f"{q.relative_to(root).as_posix()}{'/' if q.is_dir() else ''}"
                for q in target.iterdir()
            )
            return "\n".join(found) if found else f"(empty directory: {path})"
        if not target.is_file():
            return f"no such file in {skill}: {path}"

        return target.read_text(encoding="utf-8")

    @tool
    def check_classes(skill: str, path: str) -> str:
        """Check that every class="..." in a written file also appears
        somewhere in the skill's own files. A class you wrote that shows up
        nowhere in the skill was invented, not read -- fix it before finishing."""
        entry = skills.get(skill)
        if entry is None:
            return f"no such skill: {skill}. Handles: {', '.join(sorted(skills))}"
        target = resolve(workspace, path)
        if not target.is_file():
            return f"no such file: {path}"

        html = target.read_text(encoding="utf-8")
        used = set()
        for match in re.finditer(r'class=(["\'])(.*?)\1', html):
            used.update(match.group(2).split())
        if not used:
            return f"no class attributes found in {path}"

        # Read every companion file in the skill's own tree, not just its
        # SKILL.md body, since a class is more often documented in a linked
        # code.md or example than in the summary the model started from.
        corpus = "\n".join(
            p.read_text(encoding="utf-8", errors="ignore")
            for p in entry["dir"].rglob("*")
            if p.is_file()
        )
        unknown = sorted(name for name in used if name not in corpus)
        if not unknown:
            return f"all {len(used)} classes in {path} appear in {skill}'s files"
        return (
            f"{len(unknown)} of {len(used)} classes in {path} appear nowhere in "
            f"{skill}'s files, likely invented: {', '.join(unknown)}. "
            f"Read the right file with read_skill_file, then fix them."
        )

    return [
        write_file,
        read_file,
        list_files,
        load_skill,
        read_skill_file,
        check_classes,
    ]


def build_models(names):
    """One ChatOpenAI per model id, in priority order, tools left unbound.

    create_agent() binds the tools itself, so the bind_tools() call the
    create_react_agent version needed here is gone. max_retries=3 is the openai
    SDK's own retry, which already honours the provider's Retry-After.
    """
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("set OPENAI_API_KEY first")

    # No base_url: the client targets api.openai.com by default.
    return [
        ChatOpenAI(
            model=name,
            api_key=key,
            max_retries=3,
            timeout=180.0,
        )
        for name in names
    ]


def run(task, workspace, models):
    workspace.mkdir(parents=True, exist_ok=True)
    skills = discover_skills()
    tools = make_tools(workspace, skills)
    prompt = SYSTEM + skill_catalog(skills)

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
