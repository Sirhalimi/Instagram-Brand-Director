#!/usr/bin/env python3
"""Offline evidence-age audit for a dated, source-tagged Instagram knowledge file.

Read only the explicitly passed Markdown path. Emit JSON to stdout. No network,
credentials, filesystem mutation, or claims about current Meta policy.
Exit 0: no stale entries/header, including if CONFLICT/UNVERIFIED needs review.
Exit 1: at least one entry or file-level Verified date older than the limit.
Exit 2: malformed header, malformed dated entry, invalid arguments or I/O.
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

HEADER = re.compile(r"\bVerified:\s*(\d{4}-\d{2}-\d{2})\b")
TAG = re.compile(
    r"^\s*-\s+(.+?)\s+·\s+\["
    r"(OFFICIAL|REPORTED|SINGLE-SOURCE|CONFLICT|HYPOTHESIS|UNVERIFIED)"
    r"\](?=\s*(?:·|$))"
)
PREFIX_TAG = re.compile(r"^\s*-\s+\*\*\[(CONFLICT|UNVERIFIED)\]\*\*\s+(.+?)\s*$")
SUFFIX_DATE = re.compile(r"·\s*(\d{4}-\d{2}-\d{2})\s*$")
ANY_DATE = re.compile(r"·\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\s*$")

def _date(raw):
    try:
        parsed = date.fromisoformat(raw)
    except (ValueError, TypeError):
        raise ValueError("Invalid ISO date: %s" % raw) from None
    if parsed.isoformat() != raw:
        raise ValueError("Date is not exactly YYYY-MM-DD: %s" % raw)
    return parsed

def audit(text, *, today=None, max_age_days=60, path="<provided text>"):
    if not isinstance(text, str):
        raise ValueError("Knowledge content must be text")
    if type(max_age_days) is not int or max_age_days < 0:
        raise ValueError("max_age_days must be a nonnegative integer")
    day = date.today() if today is None else today
    if type(day) is not date:
        raise ValueError("today must be a date")
    result = {
        "path": str(path), "as_of": day.isoformat(), "max_age_days": max_age_days,
        "file_verified": None, "file_age_days": None, "file_stale": False,
        "entries_checked": 0, "stale_entries": [], "conflicts": [],
        "unverified": [], "undated_entries": [], "invalid_entries": [],
        "status": "CURRENT", "exit_code": 0,
    }
    header_line = None
    for lineno, line in enumerate(text.splitlines(), 1):
        found = HEADER.search(line)
        if found:
            if header_line is not None:
                raise ValueError("Multiple file-level Verified headers")
            header_line = lineno
            verified = _date(found.group(1))
            days = (day - verified).days
            if days < 0:
                raise ValueError("File-level Verified date is in the future")
            result["file_verified"] = verified.isoformat()
            result["file_age_days"] = days
            result["file_stale"] = days > max_age_days
    if header_line is None:
        raise ValueError("Missing file-level Verified: YYYY-MM-DD header")

    section = ""
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.startswith("## "):
            section = line.strip()
        match = TAG.search(line)
        if match:
            claim, tag = match.groups()
        else:
            # The supplied file also includes a prefix-tagged conflict with
            # no final date. Ignore definition bullets in the tag glossary.
            prefix = PREFIX_TAG.search(line) if section != "## Confidence tags" else None
            if prefix is None:
                continue
            tag, claim = prefix.groups()
        result["entries_checked"] += 1
        entry = {"line": lineno, "tag": tag, "claim": claim.strip()}
        tail = SUFFIX_DATE.search(line)
        if tail is None:
            entry["reason"] = "Missing final · YYYY-MM-DD segment"
            result["undated_entries"].append(entry)
        else:
            try:
                verified = _date(tail.group(1))
            except ValueError as exc:
                entry["reason"] = str(exc)
                result["invalid_entries"].append(entry)
                verified = None
            if verified is not None:
                age = (day - verified).days
                entry["verified"] = verified.isoformat()
                entry["age_days"] = age
                if age < 0:
                    entry["reason"] = "Entry date is in the future"
                    result["invalid_entries"].append(entry)
                elif age > max_age_days:
                    result["stale_entries"].append(entry)
        if tag == "CONFLICT":
            result["conflicts"].append(entry.copy())
        if tag == "UNVERIFIED":
            result["unverified"].append(entry.copy())

    # A source can be current but still require manual judgment because
    # CONFLICT and UNVERIFIED do not silently become OFFICIAL facts.
    if result["invalid_entries"]:
        result["status"] = "INVALID"
        result["exit_code"] = 2
    elif result["file_stale"] or result["stale_entries"]:
        result["status"] = "STALE"
        result["exit_code"] = 1
    elif result["conflicts"] or result["unverified"] or result["undated_entries"]:
        result["status"] = "REVIEW_REQUIRED"
    return result

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Audit dated knowledge staleness and unresolved source tags")
    parser.add_argument("knowledge_file", type=Path)
    parser.add_argument("--max-age-days", type=int, default=60)
    parser.add_argument("--as-of", type=str, help="Deterministic YYYY-MM-DD override")
    args = parser.parse_args(argv)
    try:
        day = _date(args.as_of) if args.as_of else date.today()
        result = audit(args.knowledge_file.read_text(encoding="utf-8"),
                       today=day, max_age_days=args.max_age_days,
                       path=args.knowledge_file)
    except (OSError, UnicodeError, ValueError) as error:
        result = {"path": str(args.knowledge_file), "status": "INVALID",
                  "exit_code": 2, "error": str(error)}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result["exit_code"]

if __name__ == "__main__":
    sys.exit(main())
