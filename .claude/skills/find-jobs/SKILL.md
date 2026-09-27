---
name: find-jobs
description: Search job boards for new software engineering postings, filter them against the eligibility rules and preferences in master-resume, rank survivors by LLM-judged qualification fit, and add the top matches to the Notion tracker.
disable-model-invocation: true
context: fork
agent: job-finder
argument-hint: "[optional: extra source URL to include this run]"
---

Run a full job-search pass now.

$ARGUMENTS

Harvest your configured sources: the GitHub boards and Greenhouse boards
through `.claude/scripts/fetch_boards.py`, plus Indeed if it's connected, plus
anything named above. Apply your match criteria, dedup against the tracker,
write the top-qualified matches to Notion up to the cap in `config.json`, and
report back in the summary format from your instructions.
