#!/usr/bin/env python3
"""Fail if a file shared by several skills differs between its copies.

Each skill folder must be self-contained, so shared files are copied into
every skill that uses them. Edit one copy, copy it over the others, run this.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHARED = {
    "markdown-rules.md": [
        "skills/doc-trimmer/references/markdown-rules.md",
        "skills/project-planner/references/markdown-rules.md",
    ],
    "architecture-patterns.md": [
        "skills/frontend-react/references/architecture-patterns.md",
        "skills/project-planner/references/architecture-patterns.md",
    ],
}

bad = 0
for name, copies in SHARED.items():
    texts = {}
    for rel in copies:
        p = ROOT / rel
        if not p.is_file():
            print(f"MISSING  {rel}")
            bad += 1
            continue
        texts[rel] = p.read_bytes()
    if len(set(texts.values())) > 1:
        print(f"DIFFERS  {name}: " + ", ".join(texts))
        bad += 1
    elif texts:
        print(f"ok       {name} ({len(texts)} copies)")
sys.exit(1 if bad else 0)
