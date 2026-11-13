#!/usr/bin/env python3
"""Apply the kit to a Next.js app made with create-next-app. Standard library only, Python 3.9 or later.

    python3 -I next_overlay.py APP_DIR --design PATH/design.css [--components a,b] [--sections a,b]
                               [--fonts pkg,pkg] [--html-attr name=value ...] [--replace-layout]

APP_DIR is the app's root (the folder with package.json). The script copies the kit's base CSS, motion CSS,
the Tailwind theme, the listed component and section CSS, and the project's design.css into <app>/kit/,
writes <app>/kit.css that imports them in order, and writes components/kit/Motion.tsx and ThemeScript.tsx.
With --replace-layout it also writes app/layout.tsx; without it, it prints the lines to add to your layout.

It never touches page files, and it overwrites an existing layout only with --replace-layout.
Output: OK and FAIL lines, then `RESULT  PASS` or `RESULT  FAIL`. Exit 0 on pass, 1 on fail, 2 on usage error.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent / "assets" / "kit"
BASE = ("reset.css", "tokens.css", "base.css", "direction.css", "utilities.css")
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
PKG_RE = re.compile(r"^(@[a-z0-9-]+/)?[a-z0-9][a-z0-9._-]*(/[a-z0-9._-]+)?$")


def names(text, what, fails, folder, filename):
    out = []
    for n in [x.strip() for x in (text or "").split(",") if x.strip()]:
        if not NAME_RE.match(n) or not (KIT / folder / n / filename).is_file():
            fails.append("%s %r is not in the kit (%s/<name>/%s)" % (what, n, folder, filename))
        else:
            out.append(n)
    return out


def layout_text(css_name, fonts, attrs, comment):
    imports = ['import "./%s";' % css_name] + ['import "%s";' % f for f in fonts]
    imports += ['import type { ReactNode } from "react";',
                'import { MotionRoot } from "../components/kit/Motion";',
                'import { ThemeScript } from "../components/kit/ThemeScript";']
    attr_text = "".join(" %s=%s" % (k, json.dumps(v)) for k, v in attrs)
    return "\n".join(imports) + """

// Set the page title and description from COPY.md before launch.
export const metadata = {};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en"%s suppressHydrationWarning>
      <head>
        <ThemeScript />
      </head>
      <body>
        <MotionRoot>{children}</MotionRoot>
      </body>
    </html>
  );
}
""" % attr_text


def main(argv=None):
    ap = argparse.ArgumentParser(description="Apply the kit to a create-next-app project.")
    ap.add_argument("app")
    ap.add_argument("--design", required=True, help="the project's design.css")
    ap.add_argument("--components", default="")
    ap.add_argument("--sections", default="")
    ap.add_argument("--fonts", default="", help="Fontsource packages from DESIGN.md, comma separated")
    ap.add_argument("--html-attr", action="append", default=[], help="name=value for <html>, from the Layout lines of DESIGN.md")
    ap.add_argument("--replace-layout", action="store_true")
    args = ap.parse_args(argv)

    fails, notes = [], []
    app = Path(args.app).resolve()
    pkg = app / "package.json"
    try:
        deps = json.loads(pkg.read_text(encoding="utf-8"))
        deps = {**deps.get("dependencies", {}), **deps.get("devDependencies", {})}
    except (OSError, ValueError):
        deps = {}
    if "next" not in deps:
        fails.append("%s is not a Next.js app: no `next` in package.json" % app)
    root = app / "src" if (app / "src" / "app").is_dir() else app
    appdir = root / "app"
    if not appdir.is_dir():
        fails.append("%s has no app/ folder: this overlay is for the App Router" % root)
    design = Path(args.design)
    if not design.is_file():
        fails.append("design.css not found at %s: run design-md first" % design)
    comps = names(args.components, "component", fails, "components", "component.css")
    secs = names(args.sections, "section", fails, "sections", "section.css")
    fonts = [f.strip() for f in args.fonts.split(",") if f.strip()]
    for f in fonts:
        if not PKG_RE.match(f):
            fails.append("font package %r is not a package name" % f)
    attrs = []
    for a in args.html_attr:
        k, _, v = a.partition("=")
        if not re.match(r"^[a-z][a-z0-9-]*$", k) or not v:
            fails.append("--html-attr must be name=value (got %r)" % a)
        else:
            attrs.append((k, v))
    if fails:
        for f in fails:
            print("FAIL  " + f)
        print("RESULT  FAIL")
        return 1

    kit_out = appdir / "kit"
    kit_out.mkdir(parents=True, exist_ok=True)
    imports = []
    shutil.copyfile(str(KIT / "examples" / "react" / "theme.css"), str(kit_out / "theme.css"))
    for n in BASE:
        shutil.copyfile(str(KIT / "base" / n), str(kit_out / n))
    shutil.copyfile(str(design), str(kit_out / "design.css"))
    shutil.copyfile(str(KIT / "motion" / "motion.css"), str(kit_out / "motion.css"))
    # tokens, then the project's values, then the rest; Tailwind's theme maps the variables
    imports = ["tokens.css", "design.css", "theme.css", "reset.css", "base.css", "direction.css", "utilities.css", "motion.css"]
    for n in comps:
        shutil.copyfile(str(KIT / "components" / n / "component.css"), str(kit_out / ("component-%s.css" % n)))
        imports.append("component-%s.css" % n)
    for n in secs:
        shutil.copyfile(str(KIT / "sections" / n / "section.css"), str(kit_out / ("section-%s.css" % n)))
        imports.append("section-%s.css" % n)
    (appdir / "kit.css").write_text("".join('@import "./kit/%s";\n' % i for i in imports), encoding="utf-8")

    comp_dir = root / "components" / "kit"
    comp_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(str(KIT / "examples" / "react" / "Reveal.tsx"), str(comp_dir / "Motion.tsx"))
    theme_js = (KIT / "motion" / "theme.js").read_text(encoding="utf-8")
    (comp_dir / "ThemeScript.tsx").write_text(
        "// Runs in <head> so the saved theme applies before first paint.\n"
        "const script = %s;\n\nexport function ThemeScript() {\n  return <script dangerouslySetInnerHTML={{ __html: script }} />;\n}\n" % json.dumps(theme_js),
        encoding="utf-8")

    layout = appdir / "layout.tsx"
    if args.replace_layout:
        layout.write_text(layout_text("kit.css", ["%s" % f for f in fonts], attrs, ""), encoding="utf-8")
        notes.append("layout.tsx written: set `metadata` from COPY.md")
    else:
        notes.append("add to %s: import \"./kit.css\"; wrap {children} in <MotionRoot> and put <ThemeScript /> in <head>" % layout.name)
    notes.append("install the motion package: npm install motion" + ("; fonts: npm install " + " ".join(fonts) if fonts else ""))
    notes.append("Tailwind v4 is needed for kit/theme.css; create-next-app adds it when you answer yes")
    print("OK  kit copied to %s (%d components, %d sections)" % (kit_out, len(comps), len(secs)))
    print("OK  wrote app/kit.css, components/kit/Motion.tsx, components/kit/ThemeScript.tsx")
    for n in notes:
        print("NOTE  " + n)
    print("RESULT  PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
