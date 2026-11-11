#!/usr/bin/env python3
"""Colour combos: turns 2 to 5 colours and their roles into every colour token, in light and dark.

Usage:

    python3 -I colors.py build                     rewrite assets/data/palettes.json from combos.json
    python3 -I colors.py check                     fail if palettes.json is stale or a combo fails
    python3 -I colors.py derive FILE               the role map and any choices for the user's colours
    python3 -I colors.py near FILE [--html OUT]    the 3 combos closest to the user's colours
    python3 -I colors.py suggest FG --on BG [--min 4.5]    the nearest passing shade of FG, same hue

FILE holds the user's colours, in the format in references/system/color.md. Their exact values
are kept. Shades of them are derived for secondary text, borders, surfaces and the dark theme,
and no new hue is added. A pair that fails becomes a CHOICE for the user, never a silent swap.
Output lines start with OK, CHOICE, FAIL or RESULT. Exit codes: 0 done, 1 a FAIL, 2 usage error.
"""
from __future__ import annotations

import argparse
import html
import importlib.util
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "assets" / "data"
ROLES = ("text", "background", "action", "action-2", "band", "highlight")
DECISIONS = {"shade", "large", "other", "keep"}
WHITE = (1.0, 0.0, 0.0)
MARGIN = 0.05  # derived values are rounded for CSS, so they aim a little above each minimum
USED_FOR = {
    "bg": "Page background", "surface": "Cards and panels", "surface-2": "Inputs, wells and hover fills",
    "ink": "Headings and bold text", "ink-2": "Body text", "ink-3": "Dates, captions and labels",
    "line": "Dividers", "line-strong": "Control borders", "accent": "Primary button and key emphasis",
    "on-accent": "Primary button label", "accent-soft": "Soft accent fills", "link": "Text links",
    "link-line": "Link underline", "focus": "Focus ring", "accent-2": "Second button, when the page has two distinct actions",
    "on-accent-2": "Second button label", "band": "Banded section backgrounds", "band-ink": "Headings on a band",
    "band-ink-2": "Body text on a band", "band-ink-3": "Captions on a band", "band-line": "Dividers on a band",
    "highlight": "Tags, badges and markers", "on-highlight": "Text on a highlight",
}


def contrast_module():
    spec = importlib.util.spec_from_file_location("contrast", HERE / "contrast.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---- colour maths: OKLCH <-> linear sRGB, with gamut fitting ----

def _lin(v):
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def _gam(v):
    return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def lin_to_lch(rgb):
    r, g, b = rgb
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    B = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    C = math.hypot(A, B)
    return (L, C, math.degrees(math.atan2(B, A)) % 360 if C > 1e-4 else 0.0)


def lch_to_lin(lch):
    L, C, H = lch
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def fit(lch):
    """Lowers chroma until the colour is inside sRGB, as browsers do, so contrast is measured honestly."""
    L, C, H = max(0.0, min(1.0, lch[0])), max(0.0, lch[1]), lch[2]
    while C > 0 and not all(-1e-4 <= v <= 1 + 1e-4 for v in lch_to_lin((L, C, H))):
        C = C - 0.002 if C > 0.002 else 0.0
    return (L, C, H)


def parse(value):
    value = value.strip()
    if value.startswith("#") and len(value) == 7:
        return lin_to_lch(tuple(_lin(int(value[i:i + 2], 16) / 255) for i in (1, 3, 5)))
    if value.startswith("oklch("):
        parts = value[6:].rstrip(")").replace("%", "").split()
        return (float(parts[0]) / 100, float(parts[1]), float(parts[2]))
    raise ValueError("not a #rrggbb or oklch() colour: %r" % value)


def css(lch):
    L, C, H = fit(lch)
    return "oklch(%.1f%% %.3f %.1f)" % (L * 100, C, H if C > 0.0005 else 0.0)


def hex_of(lch):
    return "#" + "".join("%02X" % round(max(0.0, min(1.0, _gam(max(0.0, min(1.0, v))))) * 255) for v in lch_to_lin(fit(lch)))


def lum(lch):
    r, g, b = (max(0.0, min(1.0, v)) for v in lch_to_lin(fit(lch)))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def mix(a, b, t):
    """t of the way from a to b, through OKLab so the hue does not swing."""
    def lab(c):
        return (c[0], c[1] * math.cos(math.radians(c[2])), c[1] * math.sin(math.radians(c[2])))
    p, q = lab(a), lab(b)
    L, A, B = (p[i] + (q[i] - p[i]) * t for i in range(3))
    C = math.hypot(A, B)
    return (L, C, math.degrees(math.atan2(B, A)) % 360 if C > 1e-4 else 0.0)


def step(base, toward, target, against, minimum):
    """The furthest point up to target from base toward a background that still passes against every surface."""
    t = target
    while t > 0:
        c = mix(base, toward, t)
        if all(ratio(c, s) >= minimum + MARGIN for s in against):
            return c
        t = round(t - 0.01, 2)
    return base


def suggest(fg, bg, minimum):
    """The nearest lightness of fg, same hue and chroma, that reaches minimum against bg."""
    best = None
    for i in range(1, 201):
        for sign in (-1, 1):
            c = fit((fg[0] + sign * i * 0.0025, fg[1], fg[2]))
            if 0 < c[0] < 1 and ratio(c, bg) >= minimum + MARGIN / 2:
                best = c
                break
        if best:
            return best
    return None


# ---- deriving a theme ----

def label_for(fill, light_options, dark):
    """Prefers a light label on a mid or dark fill and a dark one on a light fill. Returns (preferred, other)."""
    light = max(light_options, key=lambda c: ratio(c, fill))
    yellowish = 60 <= fill[2] <= 115 and fill[1] > 0.06  # yellows, ambers and limes carry dark labels
    return (dark, light) if fill[0] >= 0.68 or (yellowish and fill[0] >= 0.5) else (light, dark)


class Theme:
    def __init__(self, mode, auto):
        self.mode, self.auto = mode, auto
        self.tokens, self.choices, self.fails, self.large = {}, [], [], []

    def put(self, name, lch, exact=None):
        self.tokens[name] = exact if exact else css(lch)
        return lch

    def filled(self, name, fill, bg, ink_dark, light_options, decision, exact):
        """A filled button colour and its label. Returns the fill used."""
        on = "on-" + name
        if ratio(fill, bg) < 3.0:
            better = suggest(fill, bg, 3.0)
            if self.auto or decision == "shade":
                fill, exact = better or fill, None
            elif decision != "keep":
                self.fails.append("%s: --%s on --bg is %.2f:1 and a button needs 3:1. Options: shade %s (%.2f:1), or keep" % (self.mode, name, ratio(fill, bg), hex_of(better) if better else "none", ratio(better, bg) if better else 0))
        preferred, other = label_for(fill, light_options, ink_dark)
        if ratio(preferred, fill) >= 4.5 or decision == "keep":
            label = preferred
        elif decision == "large" and ratio(preferred, fill) >= 3.0:
            label = preferred
            self.large.append(name)
        elif self.auto or decision == "shade":
            fill, exact, label = suggest(fill, preferred, 4.5) or fill, None, preferred
        elif decision == "other" and ratio(other, fill) >= 4.5:
            label = other
        else:
            shade = suggest(fill, preferred, 4.5)
            options = ["shade %s keeps the %s label (%.2f:1)" % (hex_of(shade), "light" if preferred[0] > 0.6 else "dark", ratio(preferred, shade))] if shade else []
            if ratio(preferred, fill) >= 3.0:
                options.append("large, bold labels at 20px or more (%.2f:1, needs 3:1)" % ratio(preferred, fill))
            if ratio(other, fill) >= 4.5:
                options.append("other, a %s label (%.2f:1)" % ("light" if other[0] > 0.6 else "dark", ratio(other, fill)))
            options.append("keep, and accept %.2f:1" % ratio(preferred, fill))
            message = "%s: a %s label on --%s reads best but is %.2f:1, under 4.5:1. Options: %s" % (self.mode, "light" if preferred[0] > 0.6 else "dark", name, ratio(preferred, fill), "; ".join(options))
            if ratio(other, fill) >= 4.5:
                self.choices.append(name + ": " + message)
                label = other
            else:
                self.fails.append(message)
                label = preferred
        self.put(name, fill, exact)
        self.put(on, label)
        return fill


def build_theme(mode, c, exact, decisions, auto):
    """c holds lch colours by role; exact holds the user's strings for roles kept exactly."""
    th = Theme(mode, auto)
    text, bg = c["text"], c["background"]
    th.put("bg", bg, exact.get("background"))
    if mode == "light":
        surface = mix(bg, WHITE, 0.6) if bg[0] < 0.99 else bg
        surface2 = (bg[0] - 0.035, bg[1], bg[2])
    else:
        surface, surface2 = (bg[0] + 0.045, bg[1], bg[2]), (bg[0] + 0.09, bg[1], bg[2])
    th.put("surface", surface)
    th.put("surface-2", surface2)
    surfaces = [bg, surface, surface2]
    if min(ratio(text, s) for s in surfaces) < 4.5:
        fixed = text
        for s in surfaces:
            fixed = suggest(fixed, s, 4.5) or fixed
        if auto or decisions.get("text") == "shade":
            text, exact = fixed, dict(exact, text=None)
        elif decisions.get("text") != "keep":
            th.fails.append("%s: --ink is %.2f:1 on a surface, under 4.5:1. Options: shade %s, or keep" % (mode, min(ratio(text, s) for s in surfaces), hex_of(fixed)))
    th.put("ink", text, exact.get("text"))
    th.put("ink-2", step(text, bg, 0.30, surfaces, 4.5))
    th.put("ink-3", step(text, bg, 0.45, surfaces[:2], 4.5))
    th.put("line", mix(text, bg, 0.86))
    th.put("line-strong", step(text, bg, 0.62, surfaces[:2], 3.0))
    lights = [bg, WHITE] if mode == "light" else [text]
    dark_label = text if mode == "light" else bg
    if "action" in c:
        accent = th.filled("accent", c["action"], bg, dark_label, lights, decisions.get("on-accent"), exact.get("action"))
    else:
        accent = th.put("accent", text, exact.get("text"))
        th.put("on-accent", bg, exact.get("background"))
    soft = mix(accent, bg, 0.86)
    if ratio(text, soft) < 4.5:
        soft = mix(accent, bg, 0.93)
    th.put("accent-soft", soft)
    # Links take the action colour only when it is readable as text; otherwise ink, underlined in the action colour.
    th.tokens["link"] = th.tokens["accent"] if ratio(accent, bg) >= 4.5 else th.tokens["ink"]
    th.tokens["link-line"] = th.tokens["accent"]
    th.tokens["focus"] = th.tokens["accent"] if ratio(accent, bg) >= 3.0 else th.tokens["ink"]
    if "action-2" in c:
        th.filled("accent-2", c["action-2"], bg, dark_label, lights, decisions.get("on-accent-2"), exact.get("action-2"))
    else:
        th.tokens["accent-2"], th.tokens["on-accent-2"] = th.tokens["accent"], th.tokens["on-accent"]
    if "band" in c:
        band = c["band"]
        th.put("band", band, exact.get("band"))
        base = next((x for x in (text, bg, WHITE) if ratio(x, band) >= 4.5), None)
        if base is None:
            th.fails.append("%s: no text colour reaches 4.5:1 on --band" % mode)
            base = text
        th.put("band-ink", base, exact.get("text") if base is text else exact.get("background") if base is bg else None)
        th.put("band-ink-2", step(base, band, 0.25, [band], 4.5))
        th.put("band-ink-3", step(base, band, 0.40, [band], 4.5))
        th.put("band-line", mix(base, band, 0.82))
    else:
        for name, source in (("band", "surface"), ("band-ink", "ink"), ("band-ink-2", "ink-2"), ("band-ink-3", "ink-3"), ("band-line", "line")):
            th.tokens[name] = th.tokens[source]
    if "highlight" in c:
        hi = c["highlight"]
        th.put("highlight", hi, exact.get("highlight"))
        on = next((x for x in (text, bg, WHITE) if ratio(x, hi) >= 4.5), None)
        if on is None:
            th.fails.append("%s: no text colour reaches 4.5:1 on --highlight" % mode)
            on = text
        th.put("on-highlight", on, exact.get("text") if on is text else exact.get("background") if on is bg else None)
    else:
        th.tokens["highlight"], th.tokens["on-highlight"] = th.tokens["accent-soft"], th.tokens["ink"]
    return th


def dark_colours(c):
    """The dark theme is designed from the same hues: the dark colour becomes the page, the light one the text."""
    text, bg = c["text"], c["background"]
    d = {"background": text if text[0] <= 0.24 else (0.18, min(text[1], 0.03), text[2]),
         "text": bg if bg[0] >= 0.88 else (0.93, min(bg[1], 0.02), bg[2])}
    for role in ("action", "action-2"):
        if role in c:
            a = c[role]
            lifted = fit((max(a[0], 0.62), a[1] * 0.9, a[2]))
            d[role] = suggest(lifted, d["background"], 4.5) if ratio(lifted, d["background"]) < 4.5 else lifted
    if "band" in c:
        d["band"] = (d["background"][0] + 0.07, min(c["band"][1], 0.05), c["band"][2])
    if "highlight" in c:
        d["highlight"] = (0.36, min(c["highlight"][1] * 0.6, 0.08), c["highlight"][2])
    return d


def validate(spec):
    problems = []
    colours, roles = spec.get("colors"), spec.get("roles")
    if not isinstance(colours, dict) or not 2 <= len(colours) <= 5:
        return ["colors must name 2 to 5 colours"]
    for name, value in colours.items():
        try:
            parse(value)
        except ValueError as error:
            problems.append("%s: %s" % (name, error))
    if not isinstance(roles, dict) or not {"text", "background"} <= set(roles):
        return problems + ["roles must give at least text and background"]
    for role, name in roles.items():
        if role not in ROLES:
            problems.append("unknown role %r; roles are %s" % (role, ", ".join(ROLES)))
        elif name not in colours:
            problems.append("role %s names %r, which is not in colors" % (role, name))
    for key, value in spec.get("decisions", {}).items():
        if key not in ("text", "on-accent", "on-accent-2") or value not in DECISIONS:
            problems.append("decision %s: %s is not one of %s" % (key, value, ", ".join(sorted(DECISIONS))))
    return problems


def derive(spec):
    """Every token for both themes, plus choices and failures. The light theme keeps the given values exactly."""
    c = {role: parse(spec["colors"][name]) for role, name in spec["roles"].items()}
    exact = {role: spec["colors"][name].upper() for role, name in spec["roles"].items()}
    decisions = spec.get("decisions", {})
    light = build_theme("light", c, exact, decisions, auto=False)
    dark = build_theme("dark", dark_colours(c), {}, {}, auto=True)
    large = set(light.large)
    if "accent" in large and "action-2" not in spec["roles"]:
        large.add("accent-2")  # the second button copies the first, label and all
    return {"light": light.tokens, "dark": dark.tokens, "choices": light.choices + dark.choices,
            "fails": light.fails + dark.fails, "large": sorted(large)}


def role_map(result):
    return [(name, result["light"][name], result["dark"][name], USED_FOR[name]) for name in USED_FOR]


# ---- combos ----

def load_combos():
    return json.loads((DATA / "combos.json").read_text(encoding="utf-8"))["combos"]


def palettes_from(combos):
    out, problems = [], []
    for combo in combos:
        for p in validate(combo):
            problems.append("%s: %s" % (combo["id"], p))
        if problems:
            continue
        result = derive(combo)
        problems += ["%s: %s" % (combo["id"], f) for f in result["fails"] + result["choices"]]
        entry = {k: combo[k] for k in ("id", "name", "mood", "kinds", "audiences", "colors", "roles")}
        entry.update(size=len(combo["colors"]), light=result["light"], dark=result["dark"])
        out.append(entry)
    return out, problems


def distance(spec, combo):
    """Mean OKLab distance from each of the user's colours to the closest colour in the combo."""
    def lab(c):
        return (c[0], c[1] * math.cos(math.radians(c[2])), c[1] * math.sin(math.radians(c[2])))
    mine = [lab(parse(v)) for v in spec["colors"].values()]
    theirs = [lab(parse(v)) for v in combo["colors"].values()]
    near = [min(math.dist(m, t) for t in theirs) for m in mine]
    return sum(near) / len(near) + 0.02 * abs(len(mine) - len(theirs))


def swatch_page(entries):
    blocks = []
    for title, spec, tokens, large in entries:
        chips = "".join('<div class="chip"><span style="background:%s"></span><b>%s</b> %s</div>' % (html.escape(v), html.escape(k), html.escape(v)) for k, v in spec["colors"].items())
        t = tokens
        demo = ('<div class="demo" style="background:{bg};color:{ink}"><p style="font-size:22px;font-weight:600;margin:0">Heading in ink</p>'
                '<p style="color:{ink2};margin:6px 0 12px">Body text, with a <a style="color:{link};text-decoration-color:{line}">text link</a>.</p>'
                '<span class="b{big}" style="background:{a};color:{on}">Primary</span> {second}'
                ' <span class="tag" style="background:{hi};color:{onhi}">Tag</span>{band}</div>').format(
            bg=t["bg"], ink=t["ink"], ink2=t["ink-2"], link=t["link"], line=t["link-line"], a=t["accent"], on=t["on-accent"],
            hi=t["highlight"], onhi=t["on-highlight"], big=" big" if large else "",
            second=('<span class="b" style="background:%s;color:%s">Second action</span>' % (t["accent-2"], t["on-accent-2"])) if "action-2" in spec["roles"]
            else '<span class="b" style="box-shadow:inset 0 0 0 1px %s;color:%s">Outline</span>' % (t["line-strong"], t["ink"]),
            band=('<div class="band" style="background:%s;color:%s">A banded section</div>' % (t["band"], t["band-ink"])) if "band" in spec["roles"] else "")
        blocks.append("<section><h2>%s</h2><div class=\"chips\">%s</div>%s</section>" % (html.escape(title), chips, demo))
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><title>Colour options</title><style>"
            "body{margin:0;padding:24px;font:15px/1.4 system-ui,sans-serif;background:#fafafa;color:#111}"
            "section{margin-bottom:28px}h2{font-size:16px;margin:0 0 8px}.chips{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:10px}"
            ".chip{display:flex;align-items:center;gap:6px}.chip span{width:28px;height:28px;border-radius:4px;border:1px solid #0002}"
            ".demo{padding:20px;border-radius:6px;border:1px solid #0002}.b,.tag{display:inline-block;padding:8px 14px;border-radius:4px;font-weight:600}"
            ".tag{padding:2px 8px;font-size:13px}.big{font-size:20px;font-weight:700}.band{margin:16px -20px -20px;padding:16px 20px;border-radius:0 0 6px 6px}</style></head><body><h1 style=\"font-size:20px\">Colour options</h1>%s</body></html>\n") % "".join(blocks)


def read_spec(path):
    try:
        spec = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise SystemExit("usage error: cannot read %s: %s" % (path, error))
    return spec


def main(argv=None):
    ap = argparse.ArgumentParser(description="Colour combos and role maps for ui-craft.")
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("build")
    sub.add_parser("check")
    d = sub.add_parser("derive")
    d.add_argument("file")
    n = sub.add_parser("near")
    n.add_argument("file")
    n.add_argument("--html")
    s = sub.add_parser("suggest")
    s.add_argument("fg")
    s.add_argument("--on", required=True)
    s.add_argument("--min", type=float, default=4.5)
    try:
        args = ap.parse_args(argv)
    except SystemExit as exit_:
        return 2 if exit_.code else 0
    try:
        if args.command in ("build", "check"):
            palettes, problems = palettes_from(load_combos())
            target = DATA / "palettes.json"
            text = json.dumps({"palettes": palettes}, indent=1, ensure_ascii=False) + "\n"
            if args.command == "build" and not problems:
                target.write_text(text, encoding="utf-8")
                print("OK   wrote %d palettes to %s" % (len(palettes), target))
            if args.command == "check" and not problems and target.read_text(encoding="utf-8") != text:
                problems.append("palettes.json is out of date: run colors.py build")
            for line in problems:
                print("FAIL " + line)
            if args.command == "check" and not problems:
                print("OK   %d combos pass in light and dark" % len(palettes))
        elif args.command == "derive":
            spec = read_spec(args.file)
            problems = validate(spec)
            if problems:
                for line in problems:
                    print("usage error: " + line, file=sys.stderr)
                return 2
            result = derive(spec)
            for name, light, dark, used in role_map(result):
                print("OK   --%s  light %s  dark %s  (%s)" % (name, light, dark, used))
            for line in result["choices"]:
                print("CHOICE " + line)
            problems = result["fails"]
            for line in problems:
                print("FAIL " + line)
        elif args.command == "near":
            spec = read_spec(args.file)
            problems = validate(spec)
            if problems:
                for line in problems:
                    print("usage error: " + line, file=sys.stderr)
                return 2
            palettes = json.loads((DATA / "palettes.json").read_text(encoding="utf-8"))["palettes"]
            ranked = sorted(palettes, key=lambda p: distance(spec, p))[:3]
            for p in ranked:
                print("OK   %s (%s): %s" % (p["id"], p["name"], ", ".join("%s %s" % kv for kv in p["colors"].items())))
            if args.html:
                mine = derive(spec)
                entries = [("Your colours" + (", as they stand" if mine["choices"] else ""), spec, mine["light"], False)]
                if any(c.startswith("accent:") for c in mine["choices"]):
                    for decision, label in (("shade", "Your colours, with the nearest passing shade"), ("large", "Your colours, with large bold labels")):
                        option = derive(dict(spec, decisions=dict(spec.get("decisions", {}), **{"on-accent": decision})))
                        if not option["fails"]:
                            shown = dict(spec, colors=dict(spec["colors"]))
                            shown["colors"][spec["roles"]["action"]] = option["light"]["accent"]
                            entries.append((label, shown, option["light"], decision == "large"))
                page = swatch_page(entries + [(p["name"] + " (" + p["id"] + ")", p, p["light"], False) for p in ranked])
                Path(args.html).parent.mkdir(parents=True, exist_ok=True)
                Path(args.html).write_text(page, encoding="utf-8")
                print("OK   wrote %s" % args.html)
            problems = []
        else:
            fg, bg = parse(args.fg), parse(args.on)
            if ratio(fg, bg) >= args.min:
                print("OK   %s already passes on %s at %.2f:1" % (args.fg, args.on, ratio(fg, bg)))
                problems = []
            else:
                found = suggest(fg, bg, args.min)
                problems = [] if found else ["no shade of %s reaches %.1f:1 on %s" % (args.fg, args.min, args.on)]
                if found:
                    print("OK   %s is %.2f:1; the nearest passing shade is %s (%s) at %.2f:1" % (args.fg, ratio(fg, bg), hex_of(found), css(found), ratio(found, bg)))
                for line in problems:
                    print("FAIL " + line)
    except ValueError as error:
        print("usage error: %s" % error, file=sys.stderr)
        return 2
    print("RESULT  %s" % ("FAIL" if problems else "PASS"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
