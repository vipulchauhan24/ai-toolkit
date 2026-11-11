#!/usr/bin/env python3
"""Compares a project's design.json with recent builds, to catch a repeated look.

Usage:

    python3 -I sameness.py design.json

It scores hero, section order, section shapes, type contrast, backgrounds, headings and
image treatment against the last five builds in the history, and warns at 70% or more.
The score ignores palette and fonts on purpose: a new colour on the same page is the same page.

Options: --history FILE  --threshold 0.7
Output lines start with OK, WARN or RESULT. Exit codes: 0 done (a WARN included), 2 usage error.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from difflib import SequenceMatcher
from pathlib import Path

WEIGHTS = {"hero": 2, "order": 3, "shapes": 3, "type_contrast": 1, "backgrounds": 1, "headings": 1, "images": 1}
RECENT = 5


def facts(design):
    out = dict(design)
    if "sections" in design:
        out["order"] = ["signature" if s["shape"] == "signature" else s["id"] for s in design["sections"]]
        out["shapes"] = [s["shape"] for s in design["sections"]]
    return out


def similarity(a, b):
    """Returns the weighted match from 0 to 1, and the fields that match closely."""
    got = total = 0.0
    close = []
    for field, weight in WEIGHTS.items():
        if field not in a or field not in b:
            continue
        x, y = a[field], b[field]
        if field == "images" and "none" in (x, y):
            continue  # no pictures on one side says nothing about either look
        if field == "hero" and "custom" in (x, y):
            score = 0.0  # a hero built for the concept is never a repeat
        elif isinstance(x, list):
            score = SequenceMatcher(None, x, y).ratio()
        else:
            score = 1.0 if x == y else 0.0
        got += score * weight
        total += weight
        if score >= 0.7:
            close.append(field)
    return (got / total if total else 0.0), close


def main(argv=None):
    ap = argparse.ArgumentParser(description="Warns when a design repeats a recent build.")
    ap.add_argument("design", help="path to design.json")
    ap.add_argument("--history", default=os.path.expanduser("~/.ai-toolkit/ui-craft-history.json"))
    ap.add_argument("--threshold", type=float, default=0.7)
    args = ap.parse_args(argv)
    if not 0 < args.threshold <= 1:
        print("usage error: --threshold is above 0 and at most 1", file=sys.stderr)
        return 2
    try:
        design = json.loads(Path(args.design).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print("usage error: cannot read %s: %s" % (args.design, error), file=sys.stderr)
        return 2
    try:
        history = json.loads(Path(args.history).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        history = []
    earlier = [h for h in history if "order" in h and h.get("run") != design.get("run")][-RECENT:]
    if not earlier:
        print("OK   no earlier builds to compare with")
        print("RESULT  PASS")
        return 0
    current = facts(design)
    scored = sorted(((*similarity(current, h), h) for h in earlier), key=lambda item: item[0], reverse=True)
    score, close, entry = scored[0]
    if score >= args.threshold:
        print("WARN %d%% like the build from %s; these match: %s" % (round(score * 100), entry.get("at", "earlier"), ", ".join(close)))
        print("RESULT  WARN")
        return 0
    print("OK   closest recent build is %d%% alike" % round(score * 100))
    print("RESULT  PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
