#!/usr/bin/env python3
"""Safely stage the locally provided v0.4 ZIP in this Git checkout.

Usage:
    python3 tools/import_local_release.py /path/to/instagram-brand-director-v0.4.zip
    python3 -m unittest discover -s tests -v
    git diff --stat && git status
    git add -A && git commit -m 'feat: import full v0.4 release' && git push

This tool never stores account credentials and never performs GitHub writes itself.
"""
from pathlib import Path
from zipfile import ZipFile
import argparse
import re
import sys

SKIP = {".env", ".DS_Store"}
BLOCKED = {".git", "brands", "client-data", "secrets", "exports", "__pycache__", ".pytest_cache"}
ALLOW_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".csv", ".txt", ".toml"}
ALLOW_FILES = {"LICENSE", ".gitignore"}

def stage(archive: Path, root: Path) -> int:
    if not archive.is_file():
        raise ValueError(f"ZIP not found: {archive}")
    if not (root / "SKILL.md").exists():
        raise ValueError("Run inside the Instagram Brand Director Git checkout")
    count = 0
    with ZipFile(archive) as z:
        for item in z.infolist():
            if item.is_dir():
                continue
            parts = Path(item.filename).parts
            if not parts or parts[0] != "instagram-brand-director":
                raise ValueError(f"Unexpected archive prefix: {item.filename}")
            relative = Path(*parts[1:])
            if not relative.parts or ".." in relative.parts or relative.is_absolute():
                raise ValueError(f"Unsafe path: {item.filename}")
            if any(part in BLOCKED for part in relative.parts):
                continue
            if relative.name in SKIP or relative.name.startswith(".env"):
                continue
            if relative.suffix not in ALLOW_SUFFIXES and relative.name not in ALLOW_FILES:
                continue
            source = z.read(item)
            if len(source) > 2_000_000:
                raise ValueError(f"Unexpectedly large file: {relative}")
            if b"\x00" in source:
                raise ValueError(f"Binary file in source archive: {relative}")
            dest = root / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(source)
            count += 1
    return count

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    try:
        total = stage(args.archive.resolve(), Path(__file__).resolve().parents[1])
    except (ValueError, OSError) as exc:
        print(f"Import failed: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Staged {total} source files. Review 'git diff' and run tests before commit.")
