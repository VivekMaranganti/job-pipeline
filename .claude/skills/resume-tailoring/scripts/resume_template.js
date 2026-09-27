/**
 * One-page resume generator. resume-tailoring copies this file into a
 * per-run working directory and fills it in for one job posting.
 *
 * How to use it:
 * 1. Copy this file to a working directory unique to this run (SKILL.md step 7).
 * 2. Fill in NAME, CONTACT_LINE, and FILE_PREFIX from the master-resume
 *    skill's "Contact" section, exactly as written there.
 * 3. Fill in KEYWORDS with real terms from the job posting.
 * 4. Write the Skills, Education, Work Experience, and Projects content using
 *    ONLY facts from the master-resume skill. Reorder and cut freely; add
 *    nothing that isn't in master-resume.
 * 5. npm install docx --silent && node resume_template.js
 * 6. Render to PDF, check the page count, and look at it (SKILL.md step 8).
 *    Leave the layout constants alone on the first pass.
 *
 * Keywords: KEYWORDS tracks JD terms that also appear literally in a bullet.
 * Don't add a keyword to force a match. If the true bullet doesn't contain the
 * word, the JD isn't a real match on that point, and that belongs in the gap
 * analysis. The template never bolds a matched keyword; bolded keywords read
 * as unnatural to recruiters.
 *
 * ATS compliance: single column, tab stops (not tables) for right-aligned
 * dates, no headers, footers, images, or text boxes, and a standard font.
 * Don't add any of those even if they'd look nicer; they break ATS parsing.
 * See references/ats-checklist.md.
 */

const { Document, Packer, Paragraph, TextRun, BorderStyle } = require("docx");

// ---- Identity: copy exactly from master-resume's "Contact" section ----
const NAME = "FIRST LAST";
const CONTACT_LINE = "City, ST | Phone | Email | linkedin.com/in/handle | github.com/handle";
const FILE_PREFIX = "First_Last"; // output: <FILE_PREFIX>_Resume_<TARGET>.docx
const TARGET = "TARGET"; // company or company-role, no spaces

// ---- Layout constants (tune only if the one-page fit needs it) ----
const FONT = "Calibri"; // ATS-safe standard font; don't swap for a decorative or condensed font
const NAME_SIZE = 32; // half-points
const CONTACT_SIZE = 19;
const SECTION_SIZE = 21;
const BODY_SIZE = 20; // hard floor: never reduce below 20 (SKILL.md step 8)
const PAGE_WIDTH = 12240; // US Letter, twips
const PAGE_HEIGHT = 15840;
const MARGIN_TOP = 560; // hard floor 520
const MARGIN_BOTTOM = 560; // hard floor 520
const MARGIN_LEFT = 660; // hard floor 620
const MARGIN_RIGHT = 660; // hard floor 620
const RIGHT_TAB = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT; // keep in sync with margins

// ---- JD keywords (tracking only, never bolded) ----
// Edit per job: real terms from the actual posting.
const KEYWORDS = [
  // for example: "distributed systems", "FastAPI", "concurrent",
].sort((a, b) => b.length - a.length);

const KEYWORD_REGEX = KEYWORDS.length
  ? new RegExp("(" + KEYWORDS.map((k) => k.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|") + ")", "g")
  : null;

// Splits text on keyword matches. Every run renders identically; the split
// only exists so match tracking can be added later without touching callers.
const bodyRuns = (text) => {
  if (!KEYWORD_REGEX) return [new TextRun({ text, size: BODY_SIZE })];
  return text
    .split(KEYWORD_REGEX)
    .filter((part) => part !== "")
    .map((part) => new TextRun({ text: part, size: BODY_SIZE }));
};

const sectionHeading = (text) => new Paragraph({
  spacing: { before: 95, after: 35 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "000000" } },
  children: [new TextRun({ text, bold: true, size: SECTION_SIZE, allCaps: true })],
});

const bullet = (text) => new Paragraph({
  bullet: { level: 0 },
  spacing: { after: 20 },
  children: bodyRuns(text),
});

const jobHeader = (left, right) => new Paragraph({
  spacing: { after: 0 },
  tabStops: [{ type: "right", position: RIGHT_TAB }],
  children: [
    new TextRun({ text: left, bold: true, size: BODY_SIZE }),
    new TextRun({ text: `\t${right}`, size: BODY_SIZE }),
  ],
});

const subHeader = (left, right) => new Paragraph({
  spacing: { after: 30 },
  tabStops: [{ type: "right", position: RIGHT_TAB }],
  children: [
    new TextRun({ text: left, italics: true, size: BODY_SIZE }),
    new TextRun({ text: `\t${right}`, italics: true, size: BODY_SIZE }),
  ],
});

const para = (text, opts = {}) => new Paragraph({
  spacing: { after: 30, ...opts },
  children: [new TextRun({ text, size: BODY_SIZE })],
});

const skillLine = (label, text) => new Paragraph({
  spacing: { after: 30 },
  children: [
    new TextRun({ text: `${label}: `, bold: true, size: BODY_SIZE }),
    new TextRun({ text, size: BODY_SIZE }),
  ],
});

// ---- CONTENT: rewrite everything in `children` for the target JD ----

const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: FONT },
      },
    },
  },
  sections: [{
    properties: {
      page: {
        size: { width: PAGE_WIDTH, height: PAGE_HEIGHT },
        margin: { top: MARGIN_TOP, bottom: MARGIN_BOTTOM, left: MARGIN_LEFT, right: MARGIN_RIGHT },
      },
    },
    children: [
      new Paragraph({
        alignment: "center",
        spacing: { after: 40 },
        children: [new TextRun({ text: NAME, bold: true, size: NAME_SIZE })],
      }),
      new Paragraph({
        alignment: "center",
        spacing: { after: 120 },
        children: [new TextRun({ text: CONTACT_LINE, size: CONTACT_SIZE })],
      }),

      sectionHeading("Skills"),
      skillLine("Languages & Concepts", "REWRITE from master-resume, ordered by JD relevance"),
      skillLine("Tools & Technologies", "REWRITE from master-resume, ordered by JD relevance"),

      sectionHeading("Education"),
      jobHeader("University Name", "City, ST"),
      subHeader("Degree and Major", "Expected Month Year"),
      para("Relevant Coursework: REWRITE from master-resume, ordered by JD relevance"),

      sectionHeading("Work Experience"),
      // REWRITE from master-resume. One block per role:
      // jobHeader("Company", "City, ST"),
      // subHeader("Title", "Month Year - Month Year"),
      // bullet("..."),

      sectionHeading("Projects"),
      // REWRITE: pick, order, and word these per master-resume and the JD.
      // jobHeader("Project Name", "Month Year"),
      // subHeader("github.com/...", ""),   // omit subHeader if there's no link
      // bullet("..."),
    ],
  }],
});

Packer.toBuffer(doc).then((buf) =>
  require("fs").writeFileSync(`./${FILE_PREFIX}_Resume_${TARGET}.docx`, buf)
);

/*
Fitting to one page (see SKILL.md step 8 for the full procedure):
  node resume_template.js
  python3 "<resume-tailoring skill dir>/scripts/render_resume.py" <FILE_PREFIX>_Resume_<TARGET>.docx

If it's two pages: tighten wording, trim Skills, cut the least relevant
project, and only then reduce spacing or margins (respecting the floors).
*/
