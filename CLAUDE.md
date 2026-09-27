# job-pipeline

A Claude Code job-search pipeline. See README.md for setup. Commands:
`/find-jobs`, `/prep-apply <target>`, `/batch-prep-apply <targets>`,
`/dashboard`, `/clear-queue`, `/list-skills`.

Ground truth for anything about the user's background lives in the
`master-resume` skill (`.claude/skills/master-resume/SKILL.md`, created from
`templates/master-resume/SKILL.md` during setup). Never invent resume claims.
The wording standard lives in `writing-style`. `job-finder`, `apply-prepper`,
and `batch-apply-prepper` all read from and write to the same Notion data
source, whose ID is in `config.json`.

`/prep-apply` always stops before the final submit action. That's not
negotiable. Don't remove or soften that instruction when editing
`apply-prepper.md`. The same goes for the ban on creating accounts or
passwords and on solving CAPTCHAs.

If a standalone `apply-prepper` run stops early on a hard blocker (account
creation, a CAPTCHA) and the user later confirms they handled it manually,
resume that same agent with `SendMessage` rather than launching a fresh
`/prep-apply`. The stopped agent already has the tailored resume built and
the browser tab open where it left off. Restarting would redo the resume
build for nothing.

That rule is for a standalone `/prep-apply` run only. Inside a
`/batch-prep-apply` run, a blocked target is logged and the batch moves on
immediately, so no live agent is left to resume. Recover it with a fresh
`/prep-apply <target>`. That rebuilds the resume by default, though the user
can point the fresh run at the already-built file in `applications/<Company>/`.

Never commit personal data. `config.json`, `.claude/skills/master-resume/`,
`applications/`, and `.claude/state/` are gitignored. Keep it that way.
