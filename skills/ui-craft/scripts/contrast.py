#!/usr/bin/env python3
"""Checks text and control contrast for palettes. Standard library only.

Usage:

    python3 -I contrast.py PALETTES.json
    python3 -I contrast.py design.css

Reads OKLCH or hex values for the colour tokens and tests each pair in light and dark.
Output lines start with FAIL or RESULT. Exit codes: 0 pass, 1 a FAIL, 2 usage error.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

# foreground, background, minimum ratio
PAIRS = [
    ("ink", "bg", 4.5), ("ink", "surface", 4.5), ("ink", "surface-2", 4.5),
    ("ink-2", "bg", 4.5), ("ink-2", "surface", 4.5), ("ink-2", "surface-2", 4.5),
    ("ink-3", "bg", 4.5), ("ink-3", "surface", 4.5),
    ("on-accent", "accent", 4.5), ("ink", "accent-soft", 4.5),
    ("accent", "bg", 3.0), ("line-strong", "bg", 3.0), ("line-strong", "surface", 3.0),
]


def oklch_to_srgb(l, c, h):
    a, b = c * math.cos(math.radians(h)), c * math.sin(math.radians(h))
    lm = l + 0.3963377774 * a + 0.2158037573 * b
    mm = l - 0.1055613458 * a - 0.0638541728 * b
    sm = l - 0.0894841775 * a - 1.2914855480 * b
    lr, mr, sr = lm ** 3, mm ** 3, sm ** 3
    linear = (4.0767416621 * lr - 3.3077115913 * mr + 0.2309699292 * sr,
              -1.2684380046 * lr + 2.6097574011 * mr - 0.3413193965 * sr,
              -0.0041960863 * lr - 0.7034186147 * mr + 1.7076147010 * sr)
    return tuple(max(0.0, min(1.0, v)) for v in linear)


def parse(value):
    """Linear sRGB for an oklch() or hex colour, or None."""
    value = value.strip()
    m = re.match(r"oklch\(\s*([\d.]+)%\s+([\d.]+)\s+([\d.]+)", value)
    if m:
        return oklch_to_srgb(float(m.group(1)) / 100, float(m.group(2)), float(m.group(3)))
    m = re.fullmatch(r"#([0-9a-fA-F]{6})", value)
    if m:
        def linear(v):
            return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
        return tuple(linear(int(m.group(1)[i:i + 2], 16) / 255) for i in (0, 2, 4))
    return None


def luminance(rgb):
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def ratio(a, b):
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def check(name, tokens):
    fails = []
    for fg, bg, minimum in PAIRS:
        if fg not in tokens or bg not in tokens:
            fails.append("%s: missing token --%s or --%s" % (name, fg, bg))
            continue
        a, b = parse(tokens[fg]), parse(tokens[bg])
        if a is None or b is None:
            fails.append("%s: cannot read --%s or --%s" % (name, fg, bg))
            continue
        value = ratio(a, b)
        if value < minimum:
            fails.append("%s: --%s on --%s is %.2f:1, needs %.1f:1" % (name, fg, bg, value, minimum))
    return fails


def from_css(text):
    sets = {}
    for label, pattern in (("light", r":root\s*\{(.*?)\}"), ("dark", r'\[data-theme="dark"\]\s*\{(.*?)\}')):
        m = re.search(pattern, text, re.S)
        if m:
            sets[label] = dict(re.findall(r"--([a-z0-9-]+):\s*([^;]+);", m.group(1)))
    return sets


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1 or not Path(args[0]).is_file():
        print("usage: contrast.py PALETTES.json | design.css", file=sys.stderr)
        return 2
    path = Path(args[0])
    fails = []
    if path.suffix == ".json":
        for palette in json.loads(path.read_text(encoding="utf-8"))["palettes"]:
            for mode in ("light", "dark"):
                fails += check("%s %s" % (palette["id"], mode), palette[mode])
    else:
        sets = from_css(path.read_text(encoding="utf-8"))
        if not sets:
            print("FAIL no colour tokens found in %s" % path)
            print("RESULT  FAIL")
            return 1
        for mode, tokens in sets.items():
            fails += check(mode, tokens)
    for line in fails:
        print("FAIL " + line)
    print("RESULT  %s" % ("FAIL" if fails else "PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
