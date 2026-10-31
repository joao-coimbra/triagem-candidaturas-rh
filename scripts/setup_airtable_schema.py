"""Create/align Candidates fields on the Airtable base from .env."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def req(method: str, url: str, token: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    r = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "unifecaf-hr-screening-setup/1.0",
        },
    )
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"{method} {url} -> {e.code}: {err}") from e


def main() -> None:
    env = load_env()
    token = env["AIRTABLE_PAT"]
    base = env["AIRTABLE_BASE_ID"]
    table_id = env.get("AIRTABLE_TABLE_ID", "")

    meta = req("GET", f"https://api.airtable.com/v0/meta/bases/{base}/tables", token)
    tables = meta.get("tables", [])
    print("tables:", [t.get("name") for t in tables])

    target = None
    if table_id:
        target = next((t for t in tables if t.get("id") == table_id), None)
    if target is None:
        target = next((t for t in tables if t.get("name") == "Candidates"), None)
    if target is None and tables:
        # rename first table if empty-ish default
        target = tables[0]

    if target is None:
        raise SystemExit("No table found in base")

    print("using table:", target["name"], target["id"])
    existing = {f["name"]: f for f in target.get("fields", [])}
    print("existing fields:", sorted(existing))

    # Ensure primary field named Name
    primary = next(f for f in target["fields"] if f.get("id") == target.get("primaryFieldId"))
    if primary["name"] not in {"Name", "Nome"}:
        # can't easily rename primary via all APIs; leave as-is and map Name if exists
        print("primary field:", primary["name"])

    desired: list[dict] = [
        {"name": "Email", "type": "email"},
        {
            "name": "Job",
            "type": "singleSelect",
            "options": {
                "choices": [
                    {"name": "Full Stack Developer"},
                    {"name": "Data Analyst"},
                    {"name": "HR Assistant"},
                    {"name": "Product Designer"},
                ]
            },
        },
        {"name": "LinkedIn", "type": "url"},
        {"name": "Summary", "type": "multilineText"},
        {"name": "Resume", "type": "multipleAttachments"},
        {"name": "Score", "type": "number", "options": {"precision": 0}},
        {
            "name": "Classification",
            "type": "singleSelect",
            "options": {"choices": [{"name": "High"}, {"name": "Medium"}, {"name": "Low"}]},
        },
        {"name": "AI_Reason", "type": "multilineText"},
        {"name": "Extracted_Skills", "type": "multilineText"},
        {"name": "Suggested_Next_Step", "type": "singleLineText"},
        {
            "name": "Status",
            "type": "singleSelect",
            "options": {
                "choices": [
                    {"name": "New"},
                    {"name": "Under_Review"},
                    {"name": "Awaiting_HITL"},
                    {"name": "Approved"},
                    {"name": "Auto_Rejected"},
                    {"name": "HITL_Rejected"},
                    {"name": "Error"},
                ]
            },
        },
        {
            "name": "Human_Decision",
            "type": "singleSelect",
            "options": {
                "choices": [
                    {"name": "Pending"},
                    {"name": "Approved"},
                    {"name": "Rejected"},
                ]
            },
        },
        {"name": "Approved_By", "type": "singleLineText"},
        {"name": "Tally_Submission_Id", "type": "singleLineText"},
        {"name": "Record_URL", "type": "url"},
        {"name": "Error_Detail", "type": "multilineText"},
    ]

    # Rename primary to Name if possible
    if primary["name"] != "Name":
        try:
            req(
                "PATCH",
                f"https://api.airtable.com/v0/meta/bases/{base}/tables/{target['id']}/fields/{primary['id']}",
                token,
                {"name": "Name"},
            )
            print("renamed primary -> Name")
            existing["Name"] = primary
        except SystemExit as e:
            print("primary rename skipped:", e)

    tid = target["id"]
    for field in desired:
        if field["name"] in existing:
            print("skip exists:", field["name"])
            continue
        created = req(
            "POST",
            f"https://api.airtable.com/v0/meta/bases/{base}/tables/{tid}/fields",
            token,
            field,
        )
        print("created:", created.get("name"), created.get("type"))

    # Rename table to Candidates if needed
    if target["name"] != "Candidates":
        try:
            req(
                "PATCH",
                f"https://api.airtable.com/v0/meta/bases/{base}/tables/{tid}",
                token,
                {"name": "Candidates"},
            )
            print("renamed table -> Candidates")
        except SystemExit as e:
            print("table rename skipped:", e)

    print("DONE table_id=", tid)


if __name__ == "__main__":
    main()
