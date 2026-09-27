---
name: "resume-tailoring"
description: "Tailor the user's resume to a specific job description and produce a one-page PDF. Use this any time the user pastes or references a job description or posting and asks for a resume, wants their resume optimized or tailored for a role, asks what skills to add for a job, or asks about ATS keyword matching, even if they don't say \"resume\" explicitly (for example, \"make me a resume for this\" or \"optimize for this posting\"). Always consult the master-resume skill before writing any bullet. Never invent claims, metrics, or technologies not in it. Also consult the writing-style skill before finalizing any wording."
---

# Resume tailoring

Produces a one-page PDF resume tailored to a specific job description, built
only from real, defensible experience. The build goes through an intermediate
.docx (step 7). That .docx is a working artifact. The PDF rendered in step 8
is the deliverable.

**Default output format is PDF.** Only fall back to .docx if a specific
application portal requires it or the user asks for it. Flag that plainly,
per the ATS checklist's note on this tradeoff.

## Core rule

Every bullet must trace back to the `master-resume` skill (invoke it through
the Skill tool; it holds the ground-truth facts). Reordering, rewording,
cutting, and re-emphasizing are all expected. Inventing a metric, a
technology, a framework, or a claim that isn't in master-resume is not, even
if the job description (JD) wants it and even if it would sound better. If
the JD wants something the user doesn't have, say so plainly instead of
stretching a bullet to imply it. This includes open or unverified items in
master-resume: leave them unresolved in the tailored resume (omit or hedge
them) rather than guessing whichever version sounds best.

## Workflow

### 1. Get the job description

Take it from whatever the user pastes or references. When running unattended
(for example, inside `apply-prepper`), extract the full text from the posting
URL before doing anything else. Don't search the web to verify the posting
(live status, dates, pay) unless asked. If asked to verify, report plainly,
including when the posting looks stale or filled.

### 2. Read the master resume

Invoke the `master-resume` skill. It's the ground truth: projects, work
experience, skills, known gaps, eligibility constraints, and the user's
principles. Re-read it every time. Don't rely on memory of an earlier
session, because small errors (like C versus C++) undermine the "only claim
what you can defend" principle. Project-specific rules written in
master-resume (ownership splits, claims to avoid, required framing) override
anything general in this file.

If master-resume is missing or still full of `[BRACKETED]` placeholders,
stop and tell the user to finish README step 6.

### 3. Gap analysis

Say this out loud to the user. Don't silently adjust. Compare the JD's
requirements against master-resume and call out:

- **Strong matches:** backed by an actual project or experience line.
- **Partial or analogous matches:** true, but they need honest framing (for
  example, fault-tolerance work in one domain mapping to a JD's resilience
  ask in another).
- **Real gaps:** something the JD wants that nothing in master-resume
  supports. Name it directly. Don't bury it after a glowing summary.

The gap analysis is part of the value of this skill. Don't soften it.

### 4. Select and reorder content

- Lead with whatever's most relevant to this JD, not a fixed order.
- **Include enough content to fill the page.** A resume that stops
  three-quarters of the way down looks unfinished. Start with more projects
  rather than fewer, and cut down if it overflows. Measure the fill in step 8
  rather than guessing from a project count.
- **Cutting a project can orphan a Skills-line claim.** If a Skills line
  lists a technology whose only supporting evidence was a project you cut,
  the claim now has nothing backing it on the page. That's acceptable when
  the claim is still true, but flag it in step 9's summary.
- Cut projects or bullets that add nothing for this JD only if space
  requires it. One page is a hard constraint. State what you cut and why.
- Reword bullets to surface true keyword overlap (step 5) without changing
  what happened.
- Check master-resume's "Eligibility constraints" before committing to a
  framing. For example, the graduation date to show can depend on whether
  the posting is new-grad or internship.
- **Consult the `writing-style` skill** before finalizing any bullet wording,
  and run the wording through its self-check list.

### 5. Keyword matching for ATS

Pull real keywords from the JD (multi-word phrases and single terms, such as
"distributed systems," "FastAPI," or "RTOS") and make sure true bullets
surface that overlap in wording. Don't add a keyword to a bullet just to
include it. If the word doesn't naturally belong in a true sentence about the
work, the match is weak, and that belongs in the gap analysis, not papered
over here.

**Don't bold keywords.** Bolded keywords read as unnatural to recruiters.
`scripts/resume_template.js` never applies bold, regardless of what's in
`KEYWORDS`. Populate `KEYWORDS` with real JD terms anyway: the list still
drives wording choices.

### 6. ATS parse check

Before building the file, check the content and format against
`references/ats-checklist.md`. This is separate from keyword matching: step 5
is about which words appear, and this step is about whether an ATS can parse
the document and extract them at all. Check both content (section names, date
formats, acronyms) and template output (fonts, layout, no tables, images,
headers, or footers). Fix anything that fails before step 7.

### 7. Build the .docx

Copy `scripts/resume_template.js` to a scratch working directory **unique to
this run**. Another tailoring session might be running at the same time (for
example, two `/prep-apply` runs), so never share a working directory across
runs. Compute one run ID up front (for example, `$$`, the shell's PID) and
name the directory from it and the target, such as
`resume_<target>_<run-id>/`. Reuse the same run ID in step 8.

Fill in the template:

- `NAME`, `CONTACT_LINE`, and `FILE_PREFIX` exactly as written in
  master-resume's "Contact" section.
- The `KEYWORDS` array, and the Skills, Education, Work Experience, and
  Projects content per steps 3 to 6.

The `docx` npm module isn't preinstalled. Install it in the working directory
first:

    cd <working dir> && npm install docx --silent
    node resume_template.js

### 8. Render and look at it (mandatory)

Substitute `<FILE_PREFIX>` and `<TARGET>` with real values, and reuse the run
ID from step 7 in `-env:UserInstallation`. That flag gives each run its own
LibreOffice profile. It's required: without it, two `soffice` processes
running at once collide on the shared profile lock and one fails.

    soffice --headless -env:UserInstallation=file:///tmp/lo_profile_<run-id> --convert-to pdf <FILE_PREFIX>_Resume_<TARGET>.docx
    pdfinfo <FILE_PREFIX>_Resume_<TARGET>.pdf | grep Pages
    pdftoppm -jpeg -r 120 <FILE_PREFIX>_Resume_<TARGET>.pdf page

On macOS, if `soffice` isn't on your `PATH`, use
`/Applications/LibreOffice.app/Contents/MacOS/soffice`.

Run every command from this run's own directory, so the generic
`page-1.jpg` can't collide with another run's output.

Then **Read `page-1.jpg` and look at it.** Page count alone doesn't catch
overlapping text, a date colliding with a job title, a broken tab stop, or a
page that stops three-quarters of the way down. Don't present a file you
haven't looked at.

Also measure page fill numerically:

    python3 -c "
    from PIL import Image; im=Image.open('page-1.jpg').convert('L'); w,h=im.size; px=im.load()
    last=max((y for y in range(h) for x in range(0,w,4) if px[x,y]<200), default=0)
    print(f'fill: {100*last//h}%')"

Target 85 to 100%. Under about 80% means adding the next most JD-relevant
project or restoring a cut bullet from master-resume. Never pad, inflate
wording, or stretch spacing to fake it.

Over 100% (two pages), work through these in order:

1. **Tighten bullet wording.** Recovers the most space with no loss of
   content.
2. **Trim low-evidence entries from the Skills lines.**
3. **Cut the least JD-relevant project.** State which one and why, and check
   whether it orphaned a Skills-line claim (step 4).
4. **Only after all three, reduce spacing** (`after` on bullets,
   `before`/`after` on section headings, by 10 to 20 twips) or margins,
   keeping `RIGHT_TAB` in sync with the left and right margins.

Hard floors for step 4, for readability: `MARGIN_TOP` and `MARGIN_BOTTOM`
never below 520, `MARGIN_LEFT` and `MARGIN_RIGHT` never below 620, and
`BODY_SIZE` never below 20 (10 pt). Cut content instead.

**If any of these commands fail, stop and report the failure.** Don't
present an unverified PDF or .docx, and don't hand-write a document some
other way.

### 9. Save and summarize

Copy the final PDF to `applications/<Company>/` in the project (create the
folder if needed), next to `page-1.jpg` renamed to
`<FILE_PREFIX>_Resume_<TARGET>_preview.jpg`. Keep the .docx in the working
directory unless the user asked for .docx.

In the summary message:

- State what changed and why, tied to the JD.
- Repeat the real gaps from step 3 plainly.
- Give the measured page-fill percentage.
- If a cut project orphaned a Skills-line claim, name the claim and the
  project.
- Note anything the ATS checklist flagged that couldn't be fully resolved.
- Keep the message itself to the `writing-style` standard: plain, decisive,
  no padding.

When running unattended (inside `apply-prepper`), still do every check, but
compress the report to what that context needs: the output path, page count,
fill percentage, and real gaps.

## What not to do

- Don't fabricate metrics, frameworks, or technologies not in master-resume.
- Don't silently omit a real gap because it makes the resume look weaker.
- Don't resolve a flagged open item by picking whichever answer looks best.
  Omit or hedge it, and say so in the gap analysis.
- Don't skip the render-and-look step or the fill measurement, even when the
  content seems fine.
- Don't present a resume if the build or render commands errored.
- Don't fetch the job posting online when the user already pasted it.
- Don't let the resume exceed one page.
- Don't skip the ATS checklist (step 6) even when the resume looks good.
  Visual quality and machine-parseability are different checks.
- Don't finalize wording without running it through `writing-style`.
- Don't copy master-resume's content into this skill. It's maintained
  separately so it can change independently.
