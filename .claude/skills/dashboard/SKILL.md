---
name: dashboard
description: Show the current job pipeline status in the terminal, with counts by stage plus new matches, the ready-to-submit queue, and active interviews.
disable-model-invocation: true
allowed-tools: Bash(python3 "${CLAUDE_PROJECT_DIR}/dashboard/status.py")
---

## Pipeline status

!`python3 "${CLAUDE_PROJECT_DIR}/dashboard/status.py"`

Show the preceding output to the user as-is. Don't summarize, reformat, or
add commentary. It's already a finished status view.
