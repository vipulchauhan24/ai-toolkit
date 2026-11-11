#!/usr/bin/env python3
"""Check WCAG contrast and sRGB gamut for the semantic color tokens in a CSS file.

Usage:
  check_contrast.py <design-system-dir>       # reads <design-system-dir>/tokens.css
  check_contrast.py Harbor --pair --color-text-brand --color-surface 4.5
  check_contrast.py Harbor --hex               # print resolved hex per theme (for fallbacks)
  check_contrast.py Harbor --allow --color-primary --color-surface
                                              # known, documented exception: reported as KNOWN, not a failure

Themes: "light" = :root declarations; "dark" = light merged with overrides found in
[data-theme="dark"] blocks or @media (prefers-color-scheme: dark) blocks.
Supports hex, rgb(), oklch(), white/black/transparent-free values and var() chains.
Exit code 1 if any pair fails or any color is unparseable.
"""
import argparse
import math
import re
import sys
from pathlib import Path

# (foreground, background, minimum ratio). Text needs 4.5, non-text UI needs 3.0.
DEFAULT_PAIRS = [
    ("--color-text-primary", "--color-surface", 4.5),
    ("--color-text-secondary", "--color-surface", 4.5),
    ("--color-text-muted", "--color-surface", 4.5),
    ("--color-text-primary", "--color-surface-raised", 4.5),
    ("--color-text-secondary", "--color-surface-raised", 4.5),
    ("--color-text-muted", "--color-surface-raised", 4.5),
    ("--color-text-primary", "--color-surface-overlay", 4.5),
    ("--color-on-primary", "--color-primary", 4.5),
    ("--color-on-primary", "--color-primary-hover", 4.5),
    ("--color-on-primary", "--color-primary-active", 4.5),
    ("--color-on-success", "--color-success", 4.5),
    ("--color-on-warning", "--color-warning", 4.5),
    ("--color-on-error", "--color-error", 4.5),
    ("--color-on-info", "--color-info", 4.5),
    ("--color-primary", "--color-surface", 3.0),
    ("--color-border-strong", "--color-surface", 3.0),
    ("--color-focus-ring", "--color-surface", 3.0),
]

NAMED = {"white": (1.0, 1.0, 1.0), "black": (0.0, 0.0, 0.0)}


def strip_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def classify(stack):
    joined = " ".join(stack)
    if re.search(r"prefers-color-scheme:\s*dark|data-theme=[\"']dark[\"']", joined):
        return "dark"
    if any(s.startswith("@") for s in stack):
        return None  # other at-rules (reduced-motion, forced-colors, pointer...)
    if stack and all(":root" in s or s == "html" for s in stack):
        return "light"
    return None


def parse_tokens(css):
    themes = {"light": {}, "dark": {}}
    stack, buf = [], ""

    def flush(text):
        if ":" not in text:
            return
        name, _, value = text.partition(":")
        name, value = name.strip(), value.strip()
        if name.startswith("--"):
            theme = classify(stack)
            if theme:
                themes[theme][name] = value

    for ch in strip_comments(css):
        if ch == "{":
            stack.append(" ".join(buf.split()))
            buf = ""
        elif ch == "}":
            flush(buf)
            buf = ""
            if stack:
                stack.pop()
        elif ch == ";":
            flush(buf)
            buf = ""
        else:
            buf += ch
    dark = dict(themes["light"])
    dark.update(themes["dark"])
    return {"light": themes["light"], "dark": dark}


def resolve(value, tokens, depth=0):
    if depth > 20:
        raise ValueError("var() cycle")

    def sub(m):
        ref, fallback = m.group(1), m.group(2)
        if ref in tokens:
            return resolve(tokens[ref], tokens, depth + 1)
        if fallback:
            return resolve(fallback.strip(), tokens, depth + 1)
        raise ValueError(f"undefined token {ref}")

    prev = None
    while prev != value:
        prev = value
        value = re.sub(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*))?\)", sub, value)
    return value.strip()


def looks_like_color(value, tokens):
    try:
        v = resolve(value, tokens)
    except ValueError:
        return True  # unresolved var(): surface the error instead of hiding it
    return bool(re.match(r"(#[0-9a-f]{3,6}$|oklch\(|rgba?\(|white$|black$)", v.lower()))


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def oklch_to_linear(L, C, h):
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l_ = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (
        4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
        -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
        -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_,
    )


def num(token):
    token = token.strip()
    return float(token[:-1]) / 100 if token.endswith("%") else float(token)


def parse_color(value):
    """Return (linear_rgb tuple, in_gamut bool)."""
    v = value.strip().lower()
    if v in NAMED:
        return tuple(srgb_to_linear(c) for c in NAMED[v]), True
    m = re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})", v)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return tuple(srgb_to_linear(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)), True
    m = re.fullmatch(r"oklch\(\s*([^\s/)]+)\s+([^\s/)]+)\s+([^\s/)]+)\s*(?:/[^)]*)?\)", v)
    if m:
        L, C = num(m.group(1)), num(m.group(2))
        rgb = oklch_to_linear(L, C, float(m.group(3).replace("deg", "")))
        ok = all(-0.002 <= c <= 1.002 for c in rgb)
        return tuple(min(1.0, max(0.0, c)) for c in rgb), ok
    m = re.fullmatch(r"rgba?\(\s*(\d+)[\s,]+(\d+)[\s,]+(\d+)\s*(?:[,/][^)]*)?\)", v)
    if m:
        return tuple(srgb_to_linear(int(m.group(i)) / 255) for i in (1, 2, 3)), True
    raise ValueError(f"unsupported color syntax: {value}")


def luminance(rgb):
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def to_hex(rgb):
    def enc(c):
        c = 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
        return round(min(1.0, max(0.0, c)) * 255)
    return "#" + "".join(f"{enc(c):02x}" for c in rgb)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("design_system", help="path to the design system folder (contains tokens.css)")
    ap.add_argument("--pair", nargs=3, action="append", metavar=("FG", "BG", "MIN"),
                    help="extra pair, e.g. --pair --color-text-brand --color-surface 4.5")
    ap.add_argument("--allow", nargs=2, action="append", metavar=("FG", "BG"),
                    help="a known, documented exception: still reported, but not counted as a failure")
    ap.add_argument("--hex", action="store_true", help="print resolved hex for every color token")
    args = ap.parse_args()

    css = Path(args.design_system) / "tokens.css"
    if not css.is_file():
        ap.error(f"{css} not found")
    themes = parse_tokens(css.read_text(encoding="utf-8"))
    allowed = {(f, b) for f, b in (args.allow or [])}
    pairs = list(DEFAULT_PAIRS) + [(f, b, float(m)) for f, b, m in (args.pair or [])]
    failures = 0

    for theme, tokens in themes.items():
        print(f"== {theme} ==")
        cache = {}

        def color(name):
            if name not in cache:
                cache[name] = parse_color(resolve(tokens[name], tokens))
            return cache[name]

        for name in sorted(tokens):
            if not looks_like_color(tokens[name], tokens):
                continue
            try:
                rgb, ok = color(name)
            except ValueError as e:
                print(f"  ERROR {name}: {e}")
                failures += 1
                continue
            if not ok:
                print(f"  WARN  {name} is outside sRGB gamut (clamped); lower chroma or accept P3")
            if args.hex:
                print(f"  {name}: {to_hex(rgb)}")

        for fg, bg, minimum in pairs:
            if fg not in tokens or bg not in tokens:
                print(f"  SKIP  {fg} on {bg} (token not defined)")
                continue
            try:
                r = ratio(color(fg)[0], color(bg)[0])
            except ValueError as e:
                print(f"  ERROR {fg} on {bg}: {e}")
                failures += 1
                continue
            status = "PASS" if r >= minimum else "FAIL"
            if status == "FAIL" and (fg, bg) in allowed:
                status = "KNOWN"
            failures += status == "FAIL"
            print(f"  {status}  {fg} on {bg}: {r:.2f}:1 (need {minimum})")

    print(f"\n{failures} problem(s)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
