# ATS-Passing Checklist

Applicant Tracking Systems (Workday, Greenhouse, Lever, Taleo, iCIMS, etc.) parse
resumes into plain text before a human or a keyword filter ever sees them. A
resume can be well-written and still lose points or get mangled if the *format*
trips up that parsing step. Run every tailored resume through this list before
presenting it. This is separate from keyword matching (SKILL.md step 5) —
keyword matching is about which words appear; this is about whether the ATS can
actually extract those words correctly.

## Layout

- **Single column only.** Multi-column layouts (common in template-store
  resumes) get scrambled by many parsers — text from side-by-side columns can
  get interleaved out of order. `resume_template.js` is single-column by
  design; don't add a sidebar or a two-column skills/experience split, no
  matter how it might look on a general template.
- **No tables.** A visually table-like layout must be built with tab stops or
  spacing, not an actual Word table object — table cells parse unreliably.
  `resume_template.js`'s right-aligned dates use `tabStops`, not a table; keep
  it that way.
- **No text boxes, images, icons, or embedded graphics.** These are often
  invisible to parsers entirely — any content inside one (including a name or
  contact info someone might put in a graphic header) can simply vanish from
  the parsed text.
- **No headers or footers for anything essential.** Some parsers skip header/
  footer regions entirely. Name, contact info, and all resume content must live
  in the document body — `resume_template.js` already does this.

## Fonts and characters

- **Use a standard, widely-supported font.** Calibri, Arial, or Times New Roman.
  Avoid decorative or narrow/condensed fonts even if they help fit more text —
  a font substitution failure can silently corrupt spacing or characters.
- **Avoid special/decorative bullet characters, dividers, or symbols.** Stick to
  a standard bullet point (the template's built-in Word list bullet is fine).
  Don't use characters like ★, ➤, or custom Unicode dividers between sections.
- **Avoid non-ASCII characters where a plain equivalent exists** (smart quotes,
  em dashes in body text, etc. can sometimes render as garbage characters in
  older parsers). Plain hyphens and straight quotes are safer.

## Section headers

- **Use conventional section names**: Skills, Education, Work Experience,
  Projects. Parsers map content to resume fields by recognizing these
  headers — creative renaming ("What I Bring," "My Journey") can cause a
  section to not be recognized as what it is, even if a human would understand
  it fine.
- **Don't nest content under a header the ATS won't map** (e.g. don't bury work
  experience inside a "Career Highlights" header instead of "Work Experience").

## Dates and formatting of facts

- **Use unambiguous, parseable date formats**: "June 2026," "February 2025 -
  August 2025." Avoid slash-only formats ("6/26") that are locale-ambiguous, and
  avoid combining a date range into a single cell/table (see Layout above).
- **Spell out the first use of any non-obvious acronym**, then use the acronym
  afterward if it's also a real JD keyword. For example, write
  "retrieval-augmented generation (RAG)" in full, because the full phrase is
  often the literal JD keyword being matched, not just "RAG."
- **Keep job titles and company names in plain text**, not stylized or in a
  table — same parsing risk as above.

## File format and naming

- **Default to PDF.** Many employers state a PDF preference, and a PDF
  renders the same everywhere. The resume_template.js build still produces an
  intermediate .docx (see SKILL.md step 7); the PDF rendered in step 8 is the
  deliverable. The tradeoff: a PDF with unusual formatting can parse worse
  than .docx in some older parsers. If a specific application portal states
  a .docx preference or requirement, flag that plainly and offer .docx for
  that one instead of silently applying the default.
- **File name should be plain and identifying**: `FirstName_LastName_Resume` or
  similar, no spaces-as-special-characters issues, no version-only names like
  `resume_final_v3.pdf`. The per-role naming convention the template uses
  (`First_Last_Resume_Company.pdf`) is fine.

## Keyword placement (interacts with SKILL.md step 5)

- Keyword matching only helps if the ATS can extract the keyword at all — a
  perfectly chosen keyword sitting inside an image, table, or header is
  invisible to the parser no matter how well-chosen it is. This checklist is
  what makes step 5's keyword work actually count.
- Match the JD's exact phrasing where it's also true, not just a close synonym
  — e.g. if the JD says "REST API" and the true experience is "REST API," don't
  paraphrase it to "RESTful services" for variety; ATS keyword matching is
  frequently literal.

## Quick pass/fail gate

Before presenting the resume, confirm all of these are true:
- [ ] Single column, no tables, no text boxes, no images
- [ ] Standard font (Calibri/Arial/Times New Roman)
- [ ] Standard section headers (Skills/Education/Work Experience/Projects)
- [ ] Contact info and all content in the document body, not header/footer
- [ ] Dates in an unambiguous "Month Year" format
- [ ] File is PDF unless .docx was specifically requested or a portal requires it
- [ ] File name is plain and identifying

If any box would be unchecked, fix it before moving to step 7 in SKILL.md — or,
if the user explicitly wants a tradeoff (e.g. .docx for a specific portal), flag
the risk plainly rather than silently complying.
