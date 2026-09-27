#!/usr/bin/env python3
"""
Archive every "Not Started" row in the job application tracker.

Reads and writes directly against the Notion API (not the MCP connector,
which has no archive action) so it can run as a plain CLI command too, same
pattern as status.py.

Setup:
    export NOTION_TOKEN=secret_xxx   # Notion internal integration token,
                                      # connected to the tracker database

Usage:
    python3 clear_queue.py

Archiving is Notion's own trash mechanism, not a hard delete — cleared rows
can still be restored from Notion's trash if needed.
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


def _headers():
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def fetch_not_started_rows():
    if not NOTION_TOKEN:
        print("NOTION_TOKEN is not set. Export a Notion integration token that")
        print("has access to the tracker database (see README, step 7), then rerun.")
        sys.exit(1)

    url = f"https://api.notion.com/v1/data_sources/{load_data_source_id()}/query"
    rows = []
    payload = {
        "page_size": 100,
        "filter": {
            "property": "Application Status",
            "select": {"equals": "Not Started"},
        },
    }
    while True:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers=_headers(),
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
    return ""


def archive_page(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    req = urllib.request.Request(
        url,
        data=json.dumps({"archived": True}).encode("utf-8"),
        method="PATCH",
        headers=_headers(),
    )
    try:
        with urllib.request.urlopen(req):
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  FAILED to archive {page_id}: {e.code} {body}")
        return False


def main():
    rows = fetch_not_started_rows()

    if not rows:
        print("No 'Not Started' rows to clear.")
        return

    print(f"Archiving {len(rows)} 'Not Started' row(s)...\n")
    archived = 0
    for row in rows:
        props = row.get("properties", {})
        company = prop_text(props, "Company") or "(untitled)"
        position = prop_text(props, "Position") or "(no position)"
        if archive_page(row["id"]):
            print(f"  archived: {company} - {position}")
            archived += 1

    print(f"\nDone. Archived {archived} of {len(rows)} row(s).")
    print("These are in Notion's trash, not permanently deleted — restorable")
    print("from Notion if you archived something by mistake.")


if __name__ == "__main__":
    main()
