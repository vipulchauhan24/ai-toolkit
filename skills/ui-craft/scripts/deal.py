#!/usr/bin/env python3
"""Picks a project's design direction and writes DESIGN.md, design.json and design.css.

Usage:

    python3 -I deal.py --kind portfolio --has numbers,projects,experience,skills --out .

--has lists the real material the project has: numbers, images, portrait, projects,
experience, skills, quotes, form. A section or variant that needs something missing is
never chosen. Choices are remembered in a history file so that projects differ.

--concept FILE is a JSON file from the chosen idea (references/concept.md). Anything it
names overrules the random pick; it still cannot use material the project does not have.

Other options: --history FILE  --no-history  --seed N  --force
Output lines start with OK, FAIL or RESULT. Exit codes: 0 done, 1 failed, 2 usage error.
"""
from __future__ import annotations

import argparse
import datetime
import importlib.util
import json
import os
import random
import re
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
RECENT = 3
MATERIAL = {"numbers", "images", "portrait", "projects", "experience", "skills", "quotes", "form"}
RADII = {"sharp": "0 / 2px / 4px", "tight": "4px / 6px / 8px", "soft": "6px / 8px / 12px", "round": "8px / 12px / 20px"}
CONCEPT_KEYS = {"name", "hero", "palette", "fonts", "radius", "motion", "order", "sections", "type_contrast", "backgrounds", "headings", "images", "parallax", "signature"}
PICTURES = {"images", "portrait"}
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def contrast_module():
    spec = importlib.util.spec_from_file_location("contrast", HERE / "contrast.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load(name):
    return json.loads((ASSETS / "data" / name).read_text(encoding="utf-8"))


def available(item, has):
    return set(item.get("needs", [])) <= has


def fresh(options, key, recent, rng):
    """A random option, avoiding the most recent uses as far as the options allow."""
    for skip in range(len(recent), -1, -1):
        avoid = set(recent[len(recent) - skip:])
        unused = [o for o in options if key(o) not in avoid]
        if unused:
            return rng.choice(unused)
    return rng.choice(options)


def choose(field, options, concept, problems, rng, recent, key=lambda o: o):
    """The concept's value if it names one, otherwise a fresh random option."""
    if field not in concept:
        return fresh(options, key, recent, rng)
    match = [o for o in options if key(o) == concept[field]]
    if match:
        return match[0]
    problems.append("concept: %s %r is not available here; choose from %s" % (field, concept[field], ", ".join(str(key(o)) for o in options)))
    return options[0]


def section_order(spec, has, hero, rng):
    """Hero comes first and is not listed. The middle is shuffled, the closing sections stay last."""
    picked = []
    for section in spec["sections"]:
        if not available(section, has) or hero in section.get("skip_with_hero", []):
            continue
        if set(section.get("skip_with_section", [])) & set(picked):
            continue
        picked.append(section["id"])
    closing = spec["order"]["end"]
    middle = [s for s in picked if s not in closing]
    rng.shuffle(middle)
    leads = [s for s in middle if s in spec["order"]["lead"]]
    if leads:
        first = rng.choice(leads)
        middle.remove(first)
        middle.insert(0, first)
    return middle + [s for s in closing if s in picked]


def order_problems(ids, spec, has):
    known = {s["id"]: s for s in spec["sections"]}
    problems = []
    for sid in ids:
        if sid not in known:
            problems.append("concept: order names unknown section %r" % sid)
        elif not available(known[sid], has):
            problems.append("concept: section %s needs material this project does not have" % sid)
    if len(set(ids)) != len(ids):
        problems.append("concept: order lists a section twice")
    if not ids or ids[-1] != "footer":
        problems.append("concept: order must end with footer")
    closing = spec["order"]["end"]
    first = next((i for i, sid in enumerate(ids) if sid in closing), len(ids))
    if any(sid not in closing for sid in ids[first:]):
        problems.append("concept: only %s may follow a closing section" % ", ".join(closing))
    return problems


def choose_variants(ids, spec, has, rng, forced, problems):
    known = {s["id"]: s for s in spec["sections"]}
    for sid in forced:
        if sid not in ids:
            problems.append("concept: sections names %r, which is not on this page" % sid)
    plan = []
    previous = "hero"
    for sid in ids:
        if sid not in known:
            continue
        variants = [v for v in known[sid]["variants"] if available(v, has)]
        if not variants:
            continue
        if sid in forced:
            match = [v for v in variants if v["id"] == forced[sid]]
            if not match:
                problems.append("concept: variant %r of %s is not available; choose from %s" % (forced[sid], sid, ", ".join(v["id"] for v in variants)))
            variant = (match or variants)[0]
        else:
            different = [v for v in variants if v["shape"] != previous]
            variant = rng.choice(different or variants)
        plan.append({"id": sid, "variant": variant["id"], "shape": variant["shape"]})
        previous = variant["shape"]
    return plan


def add_signature(plan, signature, spec, has, problems):
    """Puts the one section built from scratch where the concept says it goes."""
    if not isinstance(signature, dict) or set(signature) != {"id", "after", "fallback"}:
        problems.append("concept: signature needs id, after and fallback")
        return
    sid, after, fallback = signature["id"], signature["after"], signature["fallback"]
    known = {s["id"]: s for s in spec["sections"]}
    if not isinstance(sid, str) or not SLUG.fullmatch(sid) or sid in known or sid == "hero":
        problems.append("concept: signature id must be a new lower-case-hyphen name, not %r" % (sid,))
        return
    ids = [s["id"] for s in plan]
    if after != "hero" and (after not in ids or after == "footer"):
        problems.append("concept: signature cannot follow %r" % (after,))
        return
    if fallback != "none":
        section, _, variant = str(fallback).partition("/")
        options = [v["id"] for v in known[section]["variants"] if available(v, has)] if section in known else []
        if variant not in options:
            problems.append("concept: signature fallback %r is not an available kit variant" % (fallback,))
        elif section in ids:
            problems.append("concept: signature fallback %s is already on the page; drop that section from order, or use none" % section)
    plan.insert(0 if after == "hero" else ids.index(after) + 1, {"id": sid, "variant": "signature", "shape": "signature", "fallback": fallback})


def parallax_targets(hero, plan):
    return (["hero"] if hero in ("split", "custom") else []) + [s["id"] for s in plan if s["shape"] in ("media", "signature")]


def choose_parallax(concept, hero, plan, has, motion, rng, problems):
    """At most one per page, and only where a real picture and the motion budget allow it."""
    targets = parallax_targets(hero, plan)
    blocked = None
    if not has & PICTURES:
        blocked = "it needs real images"
    elif motion == "quiet":
        blocked = "motion is quiet"
    elif any(s["variant"] == "timeline" for s in plan):
        blocked = "the timeline already uses the page's one scroll-linked element"
    if "parallax" not in concept:
        return rng.choice(targets) if targets and not blocked and rng.random() < 0.5 else None
    wanted = concept["parallax"]
    if not wanted:
        return None
    if blocked:
        problems.append("concept: parallax is not possible: " + blocked)
    elif wanted not in targets:
        problems.append("concept: parallax %r is not an image section here; choose from %s" % (wanted, ", ".join(targets) or "none"))
    return wanted


def design_css(direction, palette, fonts):
    def block(tokens):
        return "".join("  --%s: %s;\n" % item for item in tokens.items())
    return ('/* Written by deal.py. Load after the kit\'s tokens.css. */\n'
            ':root {\n  --font-display: "%s Variable", ui-sans-serif, system-ui, sans-serif;\n  --font-body: "%s Variable", ui-sans-serif, system-ui, sans-serif;\n%s}\n\n'
            '@media (prefers-color-scheme: dark) {\n  :root:not([data-theme="light"]) {\n%s  }\n}\n\n'
            ':root[data-theme="dark"] {\n%s}\n') % (
        fonts["display"], fonts["body"], block(palette["light"]),
        "".join("  " + line + "\n" for line in block(palette["dark"]).splitlines()), block(palette["dark"]))


def design_md(d, palette, fonts, kit):
    rows = "".join("| `%s` | `%s` | `%s` |\n" % (k, palette["light"][k], palette["dark"][k]) for k in palette["light"])
    def notes(section_id, fallback=None):
        items = ["signature, fallback `%s`" % fallback] if fallback else []
        return ", ".join(items + (["parallax"] if d["parallax"] == section_id else []))
    hero_note = notes("hero") or ("from the chosen preview" if d["hero"] == "custom" else "")
    plan = "| 1 | `hero` | `%s` | %s |\n" % (d["hero"], hero_note) + "".join(
        "| %d | `%s` | `%s` | %s |\n" % (i, s["id"], s["variant"], notes(s["id"], s.get("fallback"))) for i, s in enumerate(d["sections"], 2))
    concept = d.get("concept") or "none: dealt at random"
    attributes = 'data-radius="%s" data-type="%s" data-bands="%s" data-heads="%s" data-images="%s"' % (d["radius"], d["type_contrast"], d["backgrounds"], d["headings"], d["images"])
    return f"""# Design

Written by `deal.py`. Later work reads this file and does not re-decide the look. To change it, edit this file and `design.css` together.

- Kind: {d['kind']}
- Kit version: {kit}
- Material available: {', '.join(d['has']) or 'none'}
- Concept: {concept}

## Theme and atmosphere

Palette `{palette['id']}` ({palette['mood']}), type `{fonts['id']}` ({fonts['mood']}), radius family `{d['radius']}`, density `{d['density']}`.

Add one or two sentences here on how this should feel, from the fact sheet and voice in `COPY.md`.

## Colour

| Token | Light | Dark |
|---|---|---|
{rows}
Status colours and the rest use the kit's defaults.

## Typography

- Display: {fonts['display']}
- Body: {fonts['body']}
- Install: `npm install {' '.join(fonts['packages'])}`

Sizes and weights come from `references/system/typography.md`.

## Shape

Radius family `{d['radius']}` ({RADII[d['radius']]}). Density `{d['density']}`.

## Layout

Centred container with equal margins, as in `references/system/layout.md`.

Type contrast `{d['type_contrast']}`, section backgrounds `{d['backgrounds']}`, headings `{d['headings']}`, images `{d['images']}`.

Set these on `html`, and load `base/direction.css` after `base.css`:

`{attributes}`

## Sections

| Order | Section | Variant | Notes |
|---|---|---|---|
{plan}
Drop any section the fact sheet can't support. Do not add a section with no real material.

## Motion

Level `{d['motion']}`. Rules are in `references/motion/`.

## Do and don't

Do: use only kit tokens, one accent, Tabler icons, real content.

Don't: use placeholder sections, a second accent, or a layout that changes the fixed values in `references/system/system.md`.

## Responsive

Checked at 390, 768, 1024, 1440 and 1920, as `references/system/responsive.md` describes.
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description="Design direction for a ui-craft project.")
    ap.add_argument("--kind", required=True)
    ap.add_argument("--has", default="", help="comma-separated real material")
    ap.add_argument("--out", required=True, help="project root")
    ap.add_argument("--concept", help="JSON file from the chosen idea; it overrules any pick")
    ap.add_argument("--history", default=os.path.expanduser("~/.ai-toolkit/ui-craft-history.json"))
    ap.add_argument("--no-history", action="store_true", help="for a preview: leave the history unchanged")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--force", action="store_true", help="replace an existing DESIGN.md")
    args = ap.parse_args(argv)
    has = {x.strip() for x in args.has.split(",") if x.strip()}
    if has - MATERIAL:
        print("usage error: unknown material: %s" % ", ".join(sorted(has - MATERIAL)), file=sys.stderr)
        return 2
    concept = {}
    if args.concept:
        try:
            concept = json.loads(Path(args.concept).read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            print("usage error: cannot read the concept file: %s" % error, file=sys.stderr)
            return 2
        if not isinstance(concept, dict) or set(concept) - CONCEPT_KEYS:
            print("usage error: a concept is an object with only these keys: %s" % ", ".join(sorted(CONCEPT_KEYS)), file=sys.stderr)
            return 2
    kinds = load("site-kinds.json")
    if args.kind not in kinds:
        print("FAIL no design data for kind %s yet; available: %s" % (args.kind, ", ".join(kinds)))
        print("RESULT  FAIL")
        return 1
    out = Path(args.out)
    target = out / "DESIGN.md"
    if target.exists() and not args.force:
        print("FAIL %s exists: later work reads it. Use --force only if the user wants a new direction" % target)
        print("RESULT  FAIL")
        return 1

    spec = kinds[args.kind]
    history_path = Path(args.history)
    try:
        history = json.loads(history_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        history = []
    recent = history[-RECENT:]
    rng = random.Random(args.seed)
    used = lambda field: [h[field] for h in recent if field in h]
    problems = []

    heroes = [h for h in spec["heroes"] if available(h, has)]
    hero = "custom" if concept.get("hero") == "custom" else choose("hero", heroes, concept, problems, rng, used("hero"), lambda h: h["id"])["id"]
    palettes = [p for p in load("palettes.json")["palettes"] if args.kind in p["kinds"]]
    palette = choose("palette", palettes, concept, problems, rng, used("palette"), lambda p: p["id"])
    pairings = [f for f in load("fonts.json")["pairings"] if args.kind in f["kinds"]]
    matching = pairings if "fonts" in concept else [f for f in pairings if f["mood"] == palette["mood"]] or pairings
    fonts = choose("fonts", matching, concept, problems, rng, used("fonts"), lambda f: f["id"])
    radius = choose("radius", spec["radius"] if "radius" not in concept else sorted(RADII), concept, problems, rng, used("radius"))
    motion = choose("motion", spec["motion_levels"], concept, problems, rng, [])
    weights = spec["type_contrast"] if "type_contrast" in concept else [t for t in spec["type_contrast"] if hero not in t.get("skip_with_hero", [])]
    type_contrast = choose("type_contrast", weights, concept, problems, rng, used("type_contrast"), lambda t: t["id"])["id"]
    backgrounds = choose("backgrounds", spec["backgrounds"], concept, problems, rng, used("backgrounds"))
    headings = choose("headings", spec["headings"], concept, problems, rng, used("headings"))
    images = choose("images", spec["images"] if has & PICTURES else ["none"], concept, problems, rng, used("images"))

    if "order" in concept:
        ids = concept["order"]
        if not isinstance(ids, list):
            problems.append("concept: order must be a list of section ids")
            ids = []
        problems += order_problems(ids, spec, has)
    else:
        ids = section_order(spec, has, hero, rng)
    forced = concept.get("sections", {})
    if not isinstance(forced, dict):
        problems.append("concept: sections must map a section id to a variant")
        forced = {}
    sections = choose_variants(ids, spec, has, rng, forced, problems)
    if concept.get("signature"):
        add_signature(sections, concept["signature"], spec, has, problems)
    parallax = choose_parallax(concept, hero, sections, has, motion, rng, problems)
    if problems:
        for line in problems:
            print("FAIL %s" % line)
        print("RESULT  FAIL")
        return 1

    contrast = contrast_module()
    fails = contrast.check("light", palette["light"]) + contrast.check("dark", palette["dark"])
    if fails:
        for line in fails:
            print("FAIL %s" % line)
        print("RESULT  FAIL")
        return 1

    direction = {"kind": args.kind, "has": sorted(has), "hero": hero, "palette": palette["id"], "fonts": fonts["id"], "radius": radius,
                 "density": spec["density"], "motion": motion, "type_contrast": type_contrast, "backgrounds": backgrounds, "headings": headings,
                 "images": images, "parallax": parallax, "sections": sections, "concept": concept.get("name"), "run": uuid.uuid4().hex[:12]}
    kit = (ASSETS / "kit" / "VERSION").read_text(encoding="utf-8").strip()
    out.mkdir(parents=True, exist_ok=True)
    target.write_text(design_md(direction, palette, fonts, kit), encoding="utf-8")
    (out / "design.json").write_text(json.dumps(direction, indent=2) + "\n", encoding="utf-8")
    (out / "design.css").write_text(design_css(direction, palette, fonts), encoding="utf-8")

    if not args.no_history:
        entry = {k: direction[k] for k in ("hero", "palette", "fonts", "radius", "type_contrast", "backgrounds", "headings", "images", "run")}
        entry["order"] = ["signature" if s["shape"] == "signature" else s["id"] for s in sections]
        entry["shapes"] = [s["shape"] for s in sections]
        entry["at"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        history_path.parent.mkdir(parents=True, exist_ok=True)
        history_path.write_text(json.dumps(history[-20:] + [entry], indent=2) + "\n", encoding="utf-8")

    print("OK   hero %s, palette %s, fonts %s, radius %s, motion %s" % (hero, palette["id"], fonts["id"], radius, motion))
    print("OK   type %s, backgrounds %s, headings %s, images %s, parallax %s" % (type_contrast, backgrounds, headings, images, parallax or "none"))
    print("OK   sections: %s" % ", ".join("%s/%s" % (s["id"], s["variant"]) for s in direction["sections"]))
    print("OK   wrote DESIGN.md, design.json and design.css in %s" % out)
    print("RESULT  PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
