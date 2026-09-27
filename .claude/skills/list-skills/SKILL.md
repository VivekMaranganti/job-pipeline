---
name: list-skills
description: List every skill in this project, grouped into command skills (typed as slash commands) and supporting skills (invoked internally by other skills and agents).
disable-model-invocation: true
allowed-tools: Bash(python3 "${CLAUDE_PROJECT_DIR}/dashboard/list_skills.py")
---

## Skills in this project

!`python3 "${CLAUDE_PROJECT_DIR}/dashboard/list_skills.py"`

Show the preceding output to the user as-is. Don't summarize, reformat, or
add commentary. It's already a finished listing.
