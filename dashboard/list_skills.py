#!/usr/bin/env python3
"""
List every skill in this project, read live from each SKILL.md's frontmatter.

Local filesystem only, no Notion access needed.

Usage:
    python3 list_skills.py
"""

import glob
import os

PROJECT_ROOT = os.environ.get(
    "CLAUDE_PROJECT_DIR",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)


def parse_frontmatter(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}

    result = {}
    for line in parts[1].splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            quote = value[0]
            value = value[1:-1]
            if quote == '"':
                value = value.replace('\\"', '"')
        result[key] = value
    return result


def collect_skills():
    pattern = os.path.join(PROJECT_ROOT, ".claude", "skills", "*", "SKILL.md")
    commands = []
    supporting = []
    for path in sorted(glob.glob(pattern)):
        fm = parse_frontmatter(path)
        name = fm.get("name") or os.path.basename(os.path.dirname(path))
        description = fm.get("description", "")
        is_command = fm.get("disable-model-invocation", "").lower() == "true"
        (commands if is_command else supporting).append((name, description))
    return commands, supporting


def main():
    commands, supporting = collect_skills()

    print("\nSkills in this project\n" + "=" * 23)

    print("\nCommand skills (typed as slash commands)")
    print("-" * 41)
    for name, description in commands:
        print(f"/{name}")
        print(f"  {description}\n")

    print("Supporting skills (invoked internally)")
    print("-" * 39)
    for name, description in supporting:
        print(f"{name}")
        print(f"  {description}\n")


if __name__ == "__main__":
    main()
