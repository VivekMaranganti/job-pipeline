---
name: "master-resume"
description: "Ground-truth resume facts for the candidate: contact info, education, work experience, projects, skills, known gaps, eligibility constraints, and job search preferences. Read this before writing, tailoring, or verifying any resume bullet, cover letter claim, or application answer about the candidate's background. Every claim in a resume or application must trace back to something in this file. Never invent or assume beyond it. Where something is flagged \"open item,\" \"unverified,\" or \"VERIFY,\" treat it as unresolved rather than picking whichever version sounds best."
---

<!--
SETUP: This is a template. Copy it into place before your first run:

    mkdir -p .claude/skills/master-resume
    cp templates/master-resume/SKILL.md .claude/skills/master-resume/SKILL.md

Then edit the copy, not this file. The copy is gitignored so your personal
details never reach GitHub.

Replace every [BRACKETED] placeholder. Delete any section that doesn't apply
to you. Write facts, not polished resume bullets: resume-tailoring rewords
and reorders them per job. The more detail you record here (tools, numbers,
what you personally did versus what teammates did), the better the tailored
resumes get, because the agents can only claim what's written here.

You can delete this comment block once you're done.
-->

# Master resume facts: [YOUR FULL NAME]

This is the ground-truth source of everything the candidate can honestly
claim. Every bullet in a tailored resume must trace back to something here.
Rewording and reordering for relevance is fine. Inventing new claims,
technologies, or metrics is not. Where a note is flagged "open item,"
"unverified," or "VERIFY," treat it as unresolved. Don't resolve it by
picking whichever version sounds better.

## Contact

Resume header line (used exactly as written):
[Full Name] | [City, ST] | [Phone] | [Email] | [linkedin.com/in/your-handle] | [github.com/your-handle]

File name prefix for generated resumes: [First_Last]
(Resumes are saved as `[First_Last]_Resume_<Company>.pdf`.)

Full mailing address, for application forms that require a street address.
The resume header only uses city and state:
[Street, City, ST ZIP]

## Education

[University name], [City, ST]
[Degree and major], [Expected Month Year or Month Year]
GPA: [optional; delete this line if you don't want it on applications]

Relevant coursework: [Course 1, Course 2, Course 3]

## Work experience

<!-- One block per role, most recent first. Include numbers wherever you have
them, and say which ones are exact versus estimated. -->

**[Company]**, [City, ST]
[Title], [Month Year] to [Month Year]
- [What you built or did, with the tools you used and any measured result]
- [Another fact]

## Projects

<!-- One block per project. Record ownership honestly: solo or team, and on a
team project, exactly which parts were yours. The tailoring agent only claims
your parts.

Example of the level of detail that works well:

**url-shortener** (solo), github.com/jdoe/url-shortener, March 2026
Go HTTP service with a Postgres backend and a Redis read-through cache.
- Load tested with k6: 2,000 RPS at p99 18 ms on one 2-vCPU VM.
- 85 unit and integration tests; CI on GitHub Actions.
- Not deployed publicly. Runs locally with Docker Compose.
-->

**[Project name]** ([solo or team; your role]), [link], [Month Year]
[One or two sentences on what it is.]
- [Fact with tools and numbers]
- [Fact]

## Skills

<!-- Only list what you can defend in an interview. Note where the evidence
for each skill lives (which project or job), so the agent can tell when
cutting a project leaves a skill unsupported on the page. -->

**Languages:** [for example: Python (projects X, Y), TypeScript (project Z)]
**Frameworks and libraries:** [...]
**Databases:** [...]
**Infrastructure and tools:** [...]
**Concepts:** [...]

## Known gaps

<!-- Things job postings often ask for that you don't have. The agents name
these plainly in the gap analysis instead of stretching a bullet to imply
coverage. -->

- [For example: no Java framework experience (Spring, JUnit)]
- [For example: no production cloud deployment]

## Eligibility constraints

job-finder reads this section on every run to decide which postings you're
eligible for. apply-prepper uses it to answer graduation-date questions.

- **Graduation date for new-grad applications:** [Month Year]
- **Graduation date for internship and co-op applications:** [Month Year;
  same as above unless taking a co-op term pushes it later]
- **Location:** [for example: United States only, remote or on-site]
- **Experience level:** [for example: reject postings that require 1+ years
  of professional experience]

## Work authorization

apply-prepper fills these directly on application forms.

- **Authorized to work in:** [country]
- **Needs visa sponsorship now or in the future:** [Yes or No]
- **Non-compete, non-solicit, or NDA with a past employer:** [Yes or No]
- **Willing to obtain a security clearance:** [Yes, No, or leave blank]

## Voluntary EEO and demographic fields

Optional. If a field is blank, apply-prepper leaves that question for you to
answer yourself, or picks "Decline to self-identify" when that option exists.

- **Gender:** [blank or your answer]
- **Hispanic or Latino:** [blank or your answer]
- **Race:** [blank or your answer]
- **Disability status:** [blank or your answer]
- **Veteran status:** [blank or your answer]

## Start availability

- **New-grad roles:** [Month Year]
- **Internship and co-op roles:** [Month Year, or by season]

## Other dates forms ask for

- **High school graduation year:** [Year]
- **Degree start date:** [Month Year]

## Job search preferences

job-finder reads this section on every run.

- **Target application types:** [for example: new-grad full-time and
  internship/co-op software engineering roles]
- **Deprioritized (still eligible, ranked last):** [for example: Summer
  internships; or "none"]
- **Interest areas:** [optional, for example backend, infrastructure, or
  embedded. job-finder uses this only to judge fit, never to reject.]

## Principles (apply throughout)

- **Only claim what you can defend.** Every bullet must survive a direct
  interview question. No fabricated metrics, no unsupported technical claims.
- **Framing over content.** Reorder and reword to bring true relevance
  forward. Never invent new relevance.
- **Plain, direct writing.** Follow the `writing-style` skill.
- **Document limitations honestly.** When new information includes
  unverified claims, keep them flagged as open items.
