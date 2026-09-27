---
name: clear-queue
description: Archive every job still marked "Not Started" in the tracker. A bulk cleanup for postings you've decided not to pursue after reviewing what find-jobs added.
disable-model-invocation: true
allowed-tools: Bash(python3 "${CLAUDE_PROJECT_DIR}/dashboard/clear_queue.py")
---

## Clear the Not Started queue

!`python3 "${CLAUDE_PROJECT_DIR}/dashboard/clear_queue.py"`

Show the preceding output to the user as-is. Don't summarize, reformat, or
add commentary. It's already a finished report of what got archived.
