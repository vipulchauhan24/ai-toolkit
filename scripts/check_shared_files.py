#!/usr/bin/env python3
"""Check, or sync, files that are copied into several skills.

Usage:
    python3 -I scripts/check_shared_files.py          check every copy
    python3 -I scripts/check_shared_files.py --sync   overwrite copies from the canonical file

Each skill folder must be self-contained, so a file used by several skills is
copied into each one. scripts/shared_files.json lists every such file. The
first path in a list is the canonical copy: edit that one, then run --sync.

Output lines: ok / pending / MISSING / DIFFERS, then RESULT PASS or RESULT FAIL.
Exit 1 on any MISSING or DIFFERS, 0 otherwise.

pending: no copy exists yet, or the copy's skill folder does not exist yet.
MISSING: the skill folder exists but the copy does not, or the canonical file
is missing while other copies exist.
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def skill_dir(rel):
    parts = Path(rel).parts
    return ROOT / parts[0] / parts[1]


def main(argv):
    sync = "--sync" in argv
    manifest = json.loads((ROOT / "scripts" / "shared_files.json").read_text())
    bad = 0
    for entry in manifest["files"]:
        name, copies = entry["name"], entry["copies"]
        canon = ROOT / copies[0]
        existing = [c for c in copies if (ROOT / c).is_file()]
        if not existing:
            print(f"pending  {name} (no copy exists yet)")
            continue
        if not canon.is_file():
            print(f"MISSING  {copies[0]} (canonical copy; others exist: {', '.join(existing)})")
            bad += 1
            continue
        data = canon.read_bytes()
        state = "ok"
        for c in copies[1:]:
            p = ROOT / c
            if not skill_dir(c).is_dir():
                continue
            if not p.is_file() or p.read_bytes() != data:
                if sync:
                    p.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(canon, p)
                    print(f"synced   {c}")
                elif not p.is_file():
                    print(f"MISSING  {c}")
                    bad += 1
                    state = "bad"
                else:
                    print(f"DIFFERS  {c} (canonical: {copies[0]})")
                    bad += 1
                    state = "bad"
        if state == "ok":
            print(f"ok       {name}")
    print("RESULT  FAIL" if bad else "RESULT  PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
