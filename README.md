# job-pipeline

A [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) project
that runs a software engineering job search end to end:

1. **Find** new-grad and internship postings from public job boards, filter
   them against your eligibility, rank them by fit, and log the best ones to a
   Notion tracker.
2. **Prep** an application: tailor a one-page PDF resume to the posting from
   your own verified facts, open the application in Chrome, fill in every
   field, and attach the resume.
3. **Stop before submit.** You review each application and click submit
   yourself. The agents never submit, never create accounts, and never solve
   CAPTCHAs.

Nothing runs on a schedule. Every step starts when you type a command.

## Commands

| Command | What it does |
|---|---|
| `/find-jobs [url]` | Harvests job boards, filters and ranks postings, and adds the top matches to Notion as `Not Started`. An optional URL adds one extra source for this run. |
| `/prep-apply <target>` | Tailors your resume and fills one application. `<target>` is a company name from the tracker, a Notion row, or a posting URL. |
| `/batch-prep-apply [targets]` | Runs `/prep-apply` for a comma-separated list, one at a time. With no list, it processes every `Not Started` row. |
| `/dashboard` | Prints the pipeline status: counts by stage, new matches, the ready-to-submit queue, and interviews. |
| `/clear-queue` | Archives every `Not Started` row you've decided to skip. Archived rows go to Notion's trash and can be restored. |
| `/list-skills` | Lists every skill in the project. |

## How it works

```
.claude/
  agents/
    job-finder.md            Sources, filters, ranks, and writes to Notion
    apply-prepper.md         Tailors the resume and fills one application
    batch-apply-prepper.md   Runs apply-prepper over a queue, one at a time
  skills/
    find-jobs/ prep-apply/ batch-prep-apply/     Slash commands for the agents
    dashboard/ clear-queue/ list-skills/         Slash commands for the scripts
    resume-tailoring/        Builds, renders, and checks the one-page resume
    writing-style/           Wording standard for bullets and free-text answers
    master-resume/           YOUR facts (created in setup, gitignored)
  scripts/
    fetch_boards.py          Deterministic job-board harvester
  state/                     job-finder's seen-postings cache (gitignored)
dashboard/
  status.py                  /dashboard
  clear_queue.py             /clear-queue
  list_skills.py             /list-skills
templates/
  master-resume/SKILL.md     Template for your master resume
applications/                Tailored resumes land here (gitignored)
config.example.json          Copy to config.json (gitignored)
```

Some design choices that matter:

- **Your master resume is the only source of truth.** Every resume bullet and
  every form answer must trace back to `master-resume`. The agents reword and
  reorder; they don't invent. If a posting wants something you don't have,
  the gap analysis says so.
- **Board parsing is deterministic.** `fetch_boards.py` reads the raw board
  files over HTTP and parses every row itself. Summarizing large board pages
  with an LLM silently drops rows.
- **Every match gets a full posting read.** job-finder never decides from a
  title. It fetches the posting body and checks timing, location, and hidden
  experience requirements.
- **Every resume gets rendered and inspected.** resume-tailoring converts the
  resume to PDF, renders it to an image, looks at it, and measures how full the
  page is before it ships.

## Requirements

- [Claude Code](https://docs.claude.com/en/docs/claude-code/setup), recent
  enough to support subagents and skills with `context: fork`.
- A [Notion](https://www.notion.so) account (the free plan works).
- Google Chrome with the
  [Claude in Chrome](https://docs.claude.com/en/docs/claude-code/chrome)
  extension, for filling applications.
- Python 3.9 or later.
- Node.js 18 or later, for building the resume `.docx`.
- LibreOffice, for converting `.docx` to PDF.
- Poppler (`pdfinfo`, `pdftoppm`), for checking and rendering the PDF.
- Pillow, for measuring page fill.

## Setup

### 1. Install the system dependencies

macOS, with [Homebrew](https://brew.sh):

```sh
brew install node python poppler
brew install --cask libreoffice
python3 -m pip install pillow rich
```

Debian or Ubuntu:

```sh
sudo apt install nodejs npm python3 python3-pip poppler-utils libreoffice
python3 -m pip install pillow rich
```

`rich` is optional. It only makes the `/dashboard` tables nicer.

Confirm the tools are on your `PATH`:

```sh
node --version && python3 --version && pdfinfo -v && soffice --version
```

On macOS, if `soffice` isn't found, add LibreOffice to your `PATH`:

```sh
echo 'export PATH="/Applications/LibreOffice.app/Contents/MacOS:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 2. Clone the repo and create your config

```sh
git clone https://github.com/<you>/job-pipeline.git
cd job-pipeline
cp config.example.json config.json
```

`config.json` holds:

| Key | Default | Meaning |
|---|---|---|
| `notion_data_source_id` | none | Your tracker's Notion data source ID. You fill this in at step 4. |
| `max_posting_age_days` | `10` | job-finder ignores postings older than this. |
| `max_matches_per_run` | `20` | The most postings `/find-jobs` adds to Notion per run. |
| `max_concurrent_runs` | `2` | The most `/prep-apply` or `/batch-prep-apply` runs at once. Each one holds a browser tab and a LibreOffice process, so lower it to `1` on a machine with 8 GB of RAM or less. |

### 3. Create the Notion tracker

Create a new full-page database in Notion (for example, "Job Applications")
with exactly these properties. The names are case-sensitive.

| Property | Type | Options |
|---|---|---|
| `Company` | Title | |
| `Position` | Text | |
| `Application Status` | Select | `Not Started`, `Ready to Submit`, `Applied`, `Interview Scheduled`, `Offer`, `Rejected`, `Ghosted` |
| `Location` | Text | |
| `Notes` | Text | |
| `Date Applied` | Date | |

`Ready to Submit` is the status apply-prepper sets once a form is filled and
waiting for you. It must exist before you run `/prep-apply`.

Optional: after you finish step 5, you can ask Claude Code to create this
database for you with the Notion connector instead.

### 4. Add the data source ID to config.json

The agents and scripts address the database by its *data source ID*, which is
different from the page ID in the URL.

1. Open the database in Notion as a full page.
2. Click the **•••** menu at the top right, then **Manage data sources**.
3. On your data source, open its **•••** menu and click **Copy data source
   ID**.
4. Paste the ID into `config.json` as `notion_data_source_id`.

If you can't find that menu, finish step 5 first, then ask Claude Code:
`Fetch <your database URL> with the Notion connector and tell me its data
source ID.` The ID appears after `collection://` in the result.

### 5. Connect Notion to Claude Code

The agents use Notion's hosted MCP server. The server name must be `notion`,
because the agents' tool permissions reference `mcp__notion`.

```sh
claude mcp add --transport http notion https://mcp.notion.com/mcp
```

Start Claude Code in the project folder, run `/mcp`, select `notion`, and
complete the sign-in. Grant it access to the workspace that holds your
tracker.

### 6. Fill in your master resume

Copy the template into place:

```sh
mkdir -p .claude/skills/master-resume
cp templates/master-resume/SKILL.md .claude/skills/master-resume/SKILL.md
```

Edit `.claude/skills/master-resume/SKILL.md` and replace every `[BRACKETED]`
placeholder. This file drives everything:

- **Contact, Education, Work experience, Projects, Skills:** the only facts
  the resume can use. Record details, numbers, tools, and which parts of team
  projects were yours.
- **Known gaps:** things you don't have. The gap analysis names these instead
  of hiding them.
- **Eligibility constraints and Job search preferences:** how job-finder
  decides what you're eligible for and how it ranks matches.
- **Work authorization, EEO fields, Start availability:** answers
  apply-prepper fills on forms. Leave an EEO field blank if you'd rather
  answer it yourself.

Tip: you can paste your current resume into Claude Code and ask it to draft
this file from the template. Review the result line by line. Anything it gets
wrong ends up on real applications.

The copy is gitignored. Only the blank template is committed.

### 7. Set up the dashboard token

`/dashboard` and `/clear-queue` call the Notion API directly, so they need
their own token.

1. Go to [Notion integrations](https://www.notion.so/profile/integrations)
   and click **New integration**.
2. Choose your workspace, set the type to **Internal**, and save.
3. Copy the **Internal Integration Secret**.
4. Open your tracker database, click **•••**, then **Connections**, and add
   the integration.
5. Export the token in your shell profile so Claude Code inherits it:

   ```sh
   echo 'export NOTION_TOKEN=ntn_your_secret_here' >> ~/.zshrc
   source ~/.zshrc
   ```

Restart Claude Code after you set it.

### 8. Turn on browser access

apply-prepper fills applications through Claude in Chrome.

1. Install the Claude in Chrome extension and sign in.
2. Start Claude Code with `claude --chrome`, or run `/chrome` inside a
   session.

Another browser MCP server, such as Playwright, also works. apply-prepper
uses whichever browser tool the session has.

### 9. Optional: customize

- **Job sources:** edit the config block at the top of
  `.claude/scripts/fetch_boards.py`. The GitHub boards are published per
  graduating class, so update their repo names each cycle. Add the companies
  you want to watch directly to `GREENHOUSE_BOARDS`. It's empty by default.
- **Indeed:** if the Indeed connector is enabled on your claude.ai account,
  job-finder searches it too. If it isn't connected, job-finder skips it.
- **Writing style:** edit `.claude/skills/writing-style/SKILL.md` to match
  your voice.
- **Match rules:** job-finder's criteria live in `.claude/agents/job-finder.md`.

### 10. Verify the setup

Run these from the project folder:

```sh
python3 .claude/scripts/fetch_boards.py --pretty | head -40   # boards resolve
python3 dashboard/status.py                                    # Notion token and ID work
```

Then start Claude Code in the project folder and run:

```
/list-skills
/dashboard
/find-jobs
```

After `/find-jobs` adds rows, try `/prep-apply <one of the companies>` and
watch it fill the form in Chrome.

## Usage

```
/find-jobs                              # search, match, and add to Notion
/find-jobs https://example.com/careers  # same, plus one extra source
/prep-apply Example Co                  # tailor and fill one application
/batch-prep-apply                       # every "Not Started" row, one at a time
/batch-prep-apply Acme, Globex, Initech # this explicit list, in order
/dashboard                              # pipeline status
/clear-queue                            # archive every "Not Started" row
```

A typical loop:

1. Run `/find-jobs` and review the new rows in Notion.
2. Run `/batch-prep-apply` on the ones you want.
3. Review each filled form in its Chrome tab, check the free-text answers in
   the agent's report, and submit.
4. Set the row to `Applied` in Notion.
5. Run `/clear-queue` to archive the rest.

Tailored resumes are saved in `applications/<Company>/`.

### Safety rules

- The agents **never click submit**. Every application waits for you.
- The agents **never create accounts or passwords and never solve CAPTCHAs**,
  even if you tell them to. They stop, leave the tab open, and tell you what
  to do.
- The agents **only claim what your master resume supports**.

### When a run stops on a blocker

- **Standalone `/prep-apply`:** handle the blocker yourself (sign in, create
  the account, solve the CAPTCHA), then reply to the agent that it's done. It
  continues from the same tab with the resume it already built.
- **Inside `/batch-prep-apply`:** the batch logs the blocker in the row's
  `Notes` and moves on. After you handle it, run `/prep-apply <target>`
  again. To skip the rebuild, name the resume already in
  `applications/<Company>/` in your prompt.

### Running several applications

Use `/batch-prep-apply` for more than one target. Don't run `/prep-apply`
several times in a row: a second invocation of a skill that's still running
blocks your session, and the runs compete for memory. The batch processes one
target at a time and counts as one run toward `max_concurrent_runs`.

## Privacy

These paths are gitignored so your personal data stays local:

- `config.json`
- `.claude/skills/master-resume/`
- `applications/`
- `.claude/state/`

Before you push a fork, run `git status` and confirm none of them are staged.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `No Notion data source ID found` | Set `notion_data_source_id` in `config.json` (step 4). |
| `NOTION_TOKEN is not set` | Export the token (step 7) and restart Claude Code. |
| `Notion API error 404` from `/dashboard` | Connect the integration to the database (step 7, item 4), and check that you copied the data source ID, not the page ID. |
| An agent can't find Notion tools | Confirm the MCP server is named `notion` and signed in (`/mcp`). |
| `soffice: command not found` | Add LibreOffice to your `PATH` (step 1). |
| `Cannot find module 'docx'` | resume-tailoring installs it per run. Check that `npm` works. |
| A board source shows `ok: false` | The board repo was renamed or archived for the new cycle. Update its URL in `fetch_boards.py`. |
| apply-prepper can't attach the resume | Make sure the session has a browser tool (`/chrome`). It uploads through the file input, never the OS file picker. |
