#!/usr/bin/env python3
"""Skill discovery: turn a directory of SKILL.md files into agent instructions.

A skill is a folder under skills/ holding a SKILL.md, whose YAML front matter
carries a name and a one-line description:

    skills/frontend-design/SKILL.md
    ---
    name: frontend-design
    description: Visual design direction for HTML/CSS.
    ---
    # Frontend design
    ...

Only the descriptions go into the system prompt (catalog); the body is loaded
on demand by the load_skill tool. That keeps the context small when a run does
not need the skill, and full when it does.

This module shadows the skills/ directory on import: a real module wins over a
namespace package, so `import skills` inside demo_b resolves here.
"""

from pathlib import Path

SKILLS_DIR = Path(__file__).parent / "skills"


def parse_front_matter(text):
    """Split a SKILL.md into its front matter dict and its body.

    Hand-rolled rather than pyyaml, so the demo keeps its three dependencies.
    Only flat "key: value" pairs are supported, with wrapped lines indented.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text.strip()

    meta, key = {}, None
    for index, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            return meta, "\n".join(lines[index:]).strip()
        if line.startswith((" ", "\t")) and key:  # continuation of a wrapped value
            meta[key] = f"{meta[key]} {line.strip()}".strip()
        elif ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            meta[key] = value.strip()

    return {}, text.strip()  # front matter never closed: treat it all as body


def discover(directory=SKILLS_DIR):
    """Return {name: skill} for every skills/*/SKILL.md, keyed by skill name."""
    directory = Path(directory)
    skills = {}
    for path in sorted(directory.glob("*/SKILL.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        name = meta.get("name") or path.parent.name
        skills[name] = {
            "name": name,
            "description": meta.get("description", ""),
            "body": body,
            "path": path,
        }
    return skills


def catalog(skills):
    """Render the skill list appended to the system prompt.

    Empty string when no skill was found, so the prompt stays valid on a fresh
    checkout with an empty skills/ directory.
    """
    if not skills:
        return ""

    lines = [
        "",
        "",
        "Available skills. Call load_skill(name) to read one in full before",
        "doing work it covers -- do not guess at its content:",
    ]
    lines += [f"- {name}: {skills[name]['description']}" for name in sorted(skills)]
    return "\n".join(lines)


if __name__ == "__main__":
    found = discover()
    print(f"{len(found)} skill(s) in {SKILLS_DIR}")
    print(catalog(found))
