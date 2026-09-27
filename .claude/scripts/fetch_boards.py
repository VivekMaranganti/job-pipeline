#!/usr/bin/env python3
"""
Deterministic harvester for the job-finder agent.

Fetches the configured GitHub job-board markdown files and the direct-ATS
Greenhouse boards, parses every row out of the raw source (no LLM, no
summarizer in the path), and prints one normalized JSON object to stdout.

This script does fetching, parsing, and normalization ONLY. It does not judge
eligibility, does not read master-resume, and does not touch Notion. All match
judgment stays in job-finder.md.

Why it exists: job-finder used to pull these 95 KB - 1.2 MB board files through
WebFetch, which converts a page to markdown and then answers a prompt against
it with a small summarizer model. Rows were silently dropped and posting facts
were paraphrased away. Reading the raw bytes and parsing them here fixes that.

Usage:
    python3 .claude/scripts/fetch_boards.py [--max-age N] [--source NAME]
                                            [--all] [--include-closed] [--pretty]

    --max-age N        drop postings older than N days (default: max_posting_age_days
                       in config.json, or 10 if unset)
    --source NAME      run only one source (see SOURCE names below)
    --all              do not apply the age cut (still dedups)
    --include-closed   keep rows the board marks closed (default: drop them)
    --pretty           indent the JSON output

Exit status is 0 unless every source failed to fetch.

Output shape:
    {
      "generated_at": "2026-08-30T12:00:00Z",
      "params": {"max_age_days": 10, "include_closed": false},
      "sources": [
        {"name": "simplify-newgrad", "url": "...", "ok": true, "error": null,
         "raw_rows": 232, "swe_rows": 232, "kept_rows": 41}
      ],
      "postings": [
        {"company": "...", "position": "...", "location": "...", "url": "...",
         "age_days": 2, "age_raw": "2d", "source": "simplify-newgrad",
         "app_type": "new_grad", "section": "Software Engineering",
         "flags": ["no_sponsorship"], "closed": false}
      ]
    }
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

# Windows pipes default to a legacy code page; company names can contain any
# Unicode character.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# --- Source configuration -------------------------------------------------
# Keep this block in sync with the "Sources" section of
# .claude/agents/job-finder.md.
#
# The GitHub boards are published per graduating class. When a new cycle
# starts, update the repo names and file paths below (for example,
# Summer2027-Internships -> Summer2028-Internships).

MARKDOWN_SOURCES = [
    {
        "name": "speedy-newgrad",
        "kind": "speedy",
        "app_type": "new_grad",
        "url": "https://raw.githubusercontent.com/speedyapply/2027-SWE-College-Jobs/main/NEW_GRAD_USA.md",
    },
    {
        "name": "speedy-intern",
        "kind": "speedy",
        "app_type": "intern",
        "url": "https://raw.githubusercontent.com/speedyapply/2027-SWE-College-Jobs/main/README.md",
    },
    {
        "name": "simplify-newgrad",
        "kind": "simplify",
        "app_type": "new_grad",
        "url": "https://raw.githubusercontent.com/SimplifyJobs/New-Grad-Positions/dev/README.md",
    },
    {
        "name": "simplify-intern",
        "kind": "simplify",
        "app_type": "intern",
        "url": "https://raw.githubusercontent.com/SimplifyJobs/Summer2027-Internships/dev/README.md",
    },
    {
        "name": "simplify-intern-offseason",
        "kind": "simplify",
        "app_type": "intern",
        "url": "https://raw.githubusercontent.com/SimplifyJobs/Summer2027-Internships/dev/README-Off-Season.md",
    },
]

# (company display name, Greenhouse board slug)
# Empty by default. Add the companies you want to watch directly. To find a
# slug, open the company's Greenhouse job board: the slug is the path segment
# in job-boards.greenhouse.io/<slug>. Confirm it resolves with:
#   curl -s https://boards-api.greenhouse.io/v1/boards/<slug>/jobs | head -c 200
GREENHOUSE_BOARDS = [
    # ("Stripe", "stripe"),
    # ("Figma", "figma"),
]

USER_AGENT = "job-pipeline-fetch-boards/1.0"
TIMEOUT = 25
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term",
    "ref", "src", "source",
}

CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "config.json",
)


def default_max_age():
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return int(json.load(f).get("max_posting_age_days", 10))
    except (OSError, ValueError, TypeError):
        return 10


# --- HTTP ---------------------------------------------------------------------


def http_get(url):
    """GET a URL, one retry, return the decoded body as text."""
    last_err = None
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                raw = resp.read()
            return raw.decode("utf-8", errors="replace")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
            last_err = e
    raise last_err


# --- Shared helpers ---------------------------------------------------------

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")

FLAG_EMOJI = {
    "\U0001F6C2": "no_sponsorship",      # 🛂
    "\U0001F1FA\U0001F1F8": "us_citizen_required",  # 🇺🇸
    "\U0001F393": "advanced_degree",     # 🎓
    "\U0001F512": "closed",              # 🔒
}


def strip_tags(text):
    text = text.replace("<br>", " ").replace("</br>", " ").replace("<br/>", " ")
    text = _TAG_RE.sub(" ", text)
    text = (
        text.replace("&amp;", "&")
        .replace("&nbsp;", " ")
        .replace("&#39;", "'")
        .replace("&quot;", '"')
        .replace("&lt;", "<")
        .replace("&gt;", ">")
    )
    return _WS_RE.sub(" ", text).strip()


def extract_flags(text):
    return sorted({name for emoji, name in FLAG_EMOJI.items() if emoji in text})


# Structural SWE-title filter for the Greenhouse direct-ATS source. The markdown
# boards give us a "Software Engineering" section header to filter on; a raw
# Greenhouse board does not, so a title match is the equivalent cheap cut before
# the agent's full-body read. Positive-match only, deliberately permissive.
SWE_TITLE_RE = re.compile(
    r"software\s+(engineer|developer|dev\b)"
    r"|\bswe\b|\bsde\s?(i{1,3}|1|2|3)?\b"
    r"|(back|front)[\s-]?end\s+(engineer|developer|software)"
    r"|full[\s-]?stack"
    r"|firmware\s+engineer"
    r"|embedded\s+(software|systems\s+software|engineer)"
    r"|flight\s+software"
    r"|\bgnc\s+software"
    r"|ground\s+software"
    r"|platform\s+(software\s+)?engineer"
    r"|systems\s+software\s+engineer"
    r"|web\s+engineer"
    r"|mobile\s+(software\s+)?engineer"
    r"|infrastructure\s+(software\s+)?engineer"
    r"|\b(new\s+grad|early\s+career|university\s+grad|college\s+grad)\b.*\bengineer\b",
    re.IGNORECASE,
)


def clean_url(url):
    """Strip tracking query params; keep everything else (gh_jid etc.)."""
    url = url.strip().replace("&amp;", "&")
    if "?" not in url:
        return url
    base, query = url.split("?", 1)
    kept = []
    for part in query.split("&"):
        if not part:
            continue
        key = part.split("=", 1)[0].lower()
        if key in TRACKING_PARAMS:
            continue
        kept.append(part)
    return base + ("?" + "&".join(kept) if kept else "")


def parse_age_to_days(raw):
    """'1d' -> 1, '3w' -> 21, '2mo' -> 60, '1y' -> 365, '5h' -> 0. None on miss."""
    if not raw:
        return None
    m = re.search(r"(\d+)\s*(h|d|w|mo|m|y)\b", raw.strip(), re.IGNORECASE)
    if not m:
        return None
    n = int(m.group(1))
    unit = m.group(2).lower()
    if unit == "h":
        return 0
    if unit == "d":
        return n
    if unit == "w":
        return n * 7
    if unit in ("mo", "m"):
        return n * 30
    if unit == "y":
        return n * 365
    return None


def iso_age_days(iso_ts):
    if not iso_ts:
        return None
    try:
        ts = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
    except ValueError:
        return None
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - ts
    return max(0, delta.days)


# --- speedyapply parser (pipe-delimited markdown tables) -------------------


def parse_speedy(content, source):
    """speedyapply files are all SWE. Sections: FAANG+, Quant, Other."""
    postings = []
    raw_rows = 0
    section = "Software Engineering"
    section_re = re.compile(r"^###\s+(.+?)\s*$")
    table_marker_re = re.compile(r"<!--\s*TABLE_(\w+)_START")

    for line in content.splitlines():
        stripped = line.strip()
        m = section_re.match(stripped)
        if m:
            section = m.group(1)
            continue
        m = table_marker_re.search(stripped)
        if m:
            section = m.group(1).title()
            continue
        if not stripped.startswith("|"):
            continue

        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 4:
            continue
        age_raw = cells[-1]
        age_days = parse_age_to_days(age_raw)
        if age_days is None:
            continue  # header row, separator row, or malformed

        raw_rows += 1
        company = strip_tags(cells[0])
        position = strip_tags(cells[1])
        location = strip_tags(re.sub(r"\s*\+\d+\b", "", cells[2]))

        apply_url = None
        am = re.search(r'href="([^"]+)"[^>]*>\s*<img[^>]*alt="Apply"', stripped)
        if am:
            apply_url = am.group(1)
        else:
            hrefs = re.findall(r'href="([^"]+)"', stripped)
            # first href is the company link; a later one is the apply link
            if len(hrefs) >= 2:
                apply_url = hrefs[1]
            elif hrefs:
                apply_url = hrefs[0]
        if not apply_url:
            continue

        flags = extract_flags(stripped)
        closed = "closed" in flags or "\U0001F512" in stripped

        postings.append(
            {
                "company": company,
                "position": position,
                "location": location,
                "url": clean_url(apply_url),
                "age_days": age_days,
                "age_raw": age_raw,
                "source": source["name"],
                "app_type": source["app_type"],
                "section": section,
                "flags": [f for f in flags if f != "closed"],
                "closed": closed,
            }
        )

    return postings, raw_rows


# --- SimplifyJobs parser (HTML <table> inside markdown) -------------------

_TR_RE = re.compile(r"<tr>(.*?)</tr>", re.DOTALL | re.IGNORECASE)
_TD_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.DOTALL | re.IGNORECASE)
_HEADER_RE = re.compile(r"^##\s+(.*?)\s*$")


def _simplify_sections(content):
    """Yield (section_title, section_body) for each '## ...' block."""
    lines = content.splitlines()
    starts = [i for i, ln in enumerate(lines) if _HEADER_RE.match(ln.strip())]
    for idx, start in enumerate(starts):
        title = _HEADER_RE.match(lines[start].strip()).group(1)
        end = starts[idx + 1] if idx + 1 < len(starts) else len(lines)
        yield title, "\n".join(lines[start:end])


def _first_active_tbody(section_body):
    """The first <tbody>..</tbody>. Later tbodies are the 'Inactive roles' block."""
    m = re.search(r"<tbody>(.*?)</tbody>", section_body, re.DOTALL | re.IGNORECASE)
    return m.group(1) if m else ""


def parse_simplify(content, source):
    postings = []
    raw_rows = 0

    for title, body in _simplify_sections(content):
        if "software engineering" not in title.lower():
            continue
        section = "Software Engineering"
        tbody = _first_active_tbody(body)
        if not tbody:
            continue

        last_company = None
        for tr_html in _TR_RE.findall(tbody):
            tds = _TD_RE.findall(tr_html)
            if len(tds) < 5:
                continue
            raw_rows += 1
            # Column count varies: the main lists are 5-wide
            # (Company, Role, Location, Application, Age); README-Off-Season adds
            # a "Terms" column before Application. Anchor on position from the
            # front for the first three and from the back for Age; find the
            # Application cell by content.
            comp_cell, role_cell, loc_cell = tds[0], tds[1], tds[2]
            age_cell = tds[-1]
            app_cell = next(
                (c for c in tds[3:] if "href=" in c or "\U0001F512" in c),
                tds[-2],
            )

            comp_text = strip_tags(comp_cell)
            if comp_text == "↳" or comp_text == "":  # ↳ continuation
                company = last_company or "Unknown"
            else:
                am = re.search(r"<a [^>]*>(.*?)</a>", comp_cell, re.DOTALL)
                company = strip_tags(am.group(1)) if am else comp_text
                company = re.sub(r"^[^A-Za-z0-9]+", "", company).strip()
                last_company = company

            position = strip_tags(role_cell)
            location = strip_tags(re.sub(r"</?br\s*/?>", "; ", loc_cell))
            location = re.sub(r"^\d+\s+locations?\s*", "", location).strip()
            location = re.sub(r"\s*;\s*(?:;\s*)+", "; ", location).strip("; ")

            age_raw = strip_tags(age_cell)
            age_days = parse_age_to_days(age_raw)
            if age_days is None:
                continue

            flags = sorted(set(extract_flags(role_cell)) | set(extract_flags(comp_cell)))
            hrefs = re.findall(r'href="([^"]+)"', app_cell)
            direct = None
            simplify_page = None
            for h in hrefs:
                if "simplify.jobs/p/" in h:
                    simplify_page = h
                elif "simplify.jobs" not in h:
                    direct = direct or h
            url = direct or simplify_page
            closed = ("closed" in flags) or ("\U0001F512" in app_cell)
            if not url:
                if not closed:
                    continue
                url = simplify_page or ""

            postings.append(
                {
                    "company": company,
                    "position": position,
                    "location": location,
                    "url": clean_url(url) if url else "",
                    "age_days": age_days,
                    "age_raw": age_raw,
                    "source": source["name"],
                    "app_type": source["app_type"],
                    "section": section,
                    "flags": [f for f in flags if f != "closed"],
                    "closed": closed,
                }
            )

    return postings, raw_rows


# --- Greenhouse direct ATS -------------------------------------------------


def fetch_greenhouse(company, slug):
    """Returns (swe_postings, raw_job_count).

    `first_published` is the real posting date. `updated_at` is unreliable here:
    boards get bulk-re-touched, so most jobs share one recent updated_at and it
    cannot be used for the age cut. Fall back to it only when first_published is
    absent.
    """
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    body = http_get(url)
    data = json.loads(body)
    jobs = data.get("jobs", [])
    postings = []
    for job in jobs:
        title = job.get("title", "") or ""
        if not SWE_TITLE_RE.search(title):
            continue
        loc = (job.get("location") or {}).get("name", "")
        stamp = job.get("first_published") or job.get("updated_at")
        age_days = iso_age_days(stamp)
        postings.append(
            {
                "company": company,
                "position": title.strip(),
                "location": loc,
                "url": clean_url(job.get("absolute_url", "")),
                "age_days": age_days if age_days is not None else 9999,
                "age_raw": (stamp or "")[:10],
                "source": f"greenhouse:{slug}",
                "app_type": "unknown",
                "section": "direct-ats",
                "flags": [],
                "closed": False,
            }
        )
    return postings, len(jobs)


# --- Orchestration -------------------------------------------------------------


def want_source(name, only):
    return only is None or name == only


def run(max_age, only, keep_all, include_closed):
    source_reports = []
    all_postings = []
    any_ok = False

    for src in MARKDOWN_SOURCES:
        if not want_source(src["name"], only):
            continue
        report = {"name": src["name"], "url": src["url"], "ok": False,
                  "error": None, "raw_rows": 0, "swe_rows": 0, "kept_rows": 0}
        try:
            content = http_get(src["url"])
        except Exception as e:  # noqa: BLE001 - report and continue
            report["error"] = f"{type(e).__name__}: {e}"
            source_reports.append(report)
            continue
        any_ok = True
        parser = parse_speedy if src["kind"] == "speedy" else parse_simplify
        postings, raw_rows = parser(content, src)
        report["ok"] = True
        report["raw_rows"] = raw_rows
        report["swe_rows"] = len(postings)
        kept = _apply_cuts(postings, max_age, keep_all, include_closed)
        report["kept_rows"] = len(kept)
        all_postings.extend(kept)
        source_reports.append(report)

    for company, slug in GREENHOUSE_BOARDS:
        name = f"greenhouse:{slug}"
        if not want_source(name, only):
            continue
        report = {"name": name, "url": f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
                  "ok": False, "error": None, "raw_rows": 0, "swe_rows": 0, "kept_rows": 0}
        try:
            postings, raw_rows = fetch_greenhouse(company, slug)
        except Exception as e:  # noqa: BLE001
            report["error"] = f"{type(e).__name__}: {e}"
            source_reports.append(report)
            continue
        any_ok = True
        report["ok"] = True
        report["raw_rows"] = raw_rows  # every posting on the board
        report["swe_rows"] = len(postings)  # after SWE-title structural cut
        kept = _apply_cuts(postings, max_age, keep_all, include_closed)
        report["kept_rows"] = len(kept)
        all_postings.extend(kept)
        source_reports.append(report)

    deduped = _dedup(all_postings)
    deduped.sort(key=lambda p: (p["age_days"], p["company"].lower()))

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "params": {"max_age_days": max_age, "include_closed": include_closed,
                   "age_cut_applied": not keep_all},
        "sources": source_reports,
        "postings": deduped,
    }, any_ok


def _apply_cuts(postings, max_age, keep_all, include_closed):
    out = []
    for p in postings:
        if not include_closed and p.get("closed"):
            continue
        if not keep_all and p["age_days"] is not None and p["age_days"] > max_age:
            continue
        out.append(p)
    return out


def _dedup(postings):
    seen = {}
    for p in postings:
        key = p["url"].lower().rstrip("/") or f'{p["company"].lower()}|{p["position"].lower()}'
        if key not in seen:
            seen[key] = p
    return list(seen.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max-age", type=int, default=default_max_age(), help="drop postings older than N days")
    ap.add_argument("--source", default=None, help="run only this source by name")
    ap.add_argument("--all", action="store_true", help="skip the age cut")
    ap.add_argument("--include-closed", action="store_true", help="keep closed rows")
    ap.add_argument("--pretty", action="store_true", help="indent JSON")
    args = ap.parse_args()

    result, any_ok = run(args.max_age, args.source, args.all, args.include_closed)
    json.dump(result, sys.stdout, indent=2 if args.pretty else None)
    sys.stdout.write("\n")

    if not any_ok:
        sys.stderr.write("fetch_boards: every source failed to fetch\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
