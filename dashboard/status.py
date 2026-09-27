#!/usr/bin/env python3
"""
Terminal status view for the job application tracker.

Reads directly from the Notion API (not the MCP connector) so it can run as a
plain CLI command outside a Claude Code session too.

Setup:
    export NOTION_TOKEN=secret_xxx   # Notion internal integration token,
                                      # connected to the tracker database
    pip install rich                 # optional; stdlib-only fallback otherwise

Usage:
    python3 status.py
"""

import os
import sys
import urllib.request
import urllib.error
import json

# Windows pipes default to a legacy code page; company names can contain any
# Unicode character.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

NOTION_VERSION = "2025-09-03"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")


def load_data_source_id():
    """NOTION_JOB_TRACKER_DATA_SOURCE_ID wins; otherwise read config.json."""
    env = os.environ.get("NOTION_JOB_TRACKER_DATA_SOURCE_ID")
    if env:
        return env
    path = os.path.join(PROJECT_ROOT, "config.json")
    try:
        with open(path, encoding="utf-8") as f:
            value = json.load(f).get("notion_data_source_id", "")
    except (OSError, ValueError):
        value = ""
    if not value or value.startswith("PASTE"):
        print("No Notion data source ID found. Set notion_data_source_id in")
        print("config.json (see README, step 4), then rerun.")
        sys.exit(1)
    return value

STATUS_ORDER = [
    "Not Started",
    "Ready to Submit",
    "Applied",
    "Interview Scheduled",
    "Offer",
    "Rejected",
    "Ghosted",
]


def fetch_rows():
    if not NOTION_TOKEN:
        print("NOTION_TOKEN is not set. Export a Notion integration token that")
        print("has access to the tracker database (see README, step 7), then rerun.")
        sys.exit(1)

    url = f"https://api.notion.com/v1/data_sources/{load_data_source_id()}/query"
    rows = []
    payload = {"page_size": 100}
    while True:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {NOTION_TOKEN}",
                "Notion-Version": NOTION_VERSION,
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"Notion API error {e.code}: {body}")
            sys.exit(1)

        rows.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]

    return rows


def prop_text(props, name):
    prop = props.get(name)
    if not prop:
        return ""
    ptype = prop.get("type")
    if ptype == "title":
        return "".join(t.get("plain_text", "") for t in prop.get("title", []))
    if ptype == "rich_text":
        return "".join(t.get("plain_text", "") for t in prop.get("rich_text", []))
    if ptype == "select":
        sel = prop.get("select")
        return sel.get("name", "") if sel else ""
    if ptype == "date":
        d = prop.get("date")
        return d.get("start", "") if d else ""
    return ""


def render(rows):
    by_status = {s: [] for s in STATUS_ORDER}
    for row in rows:
        props = row.get("properties", {})
        status = prop_text(props, "Application Status") or "Not Started"
        by_status.setdefault(status, []).append(
            {
                "company": prop_text(props, "Company") or "(untitled)",
                "position": prop_text(props, "Position"),
                "date": prop_text(props, "Date Applied"),
            }
        )

    try:
        from rich.console import Console
        from rich.table import Table

        console = Console()
        console.print("\n[bold]Job Pipeline Status[/bold]\n")

        counts = Table(show_header=False, box=None, padding=(0, 2))
        for status in STATUS_ORDER:
            n = len(by_status.get(status, []))
            if n:
                counts.add_row(status, str(n))
        console.print(counts)

        for status in ["Not Started", "Ready to Submit", "Interview Scheduled"]:
            entries = by_status.get(status, [])
            if not entries:
                continue
            console.print(f"\n[bold]{status}[/bold]")
            table = Table(show_header=True, header_style="bold")
            table.add_column("Company")
            table.add_column("Position")
            table.add_column("Date")
            for e in entries:
                table.add_row(e["company"], e["position"], e["date"])
            console.print(table)
        console.print()
        return
    except ImportError:
        pass

    # Plain-text fallback, no dependencies beyond the standard library.
    print("\nJob Pipeline Status\n" + "=" * 20)
    for status in STATUS_ORDER:
        n = len(by_status.get(status, []))
        if n:
            print(f"{status:22} {n}")

    for status in ["Not Started", "Ready to Submit", "Interview Scheduled"]:
        entries = by_status.get(status, [])
        if not entries:
            continue
        print(f"\n{status}\n" + "-" * len(status))
        for e in entries:
            print(f"  {e['company']:25} {e['position']:40} {e['date']}")
    print()


if __name__ == "__main__":
    render(fetch_rows())
