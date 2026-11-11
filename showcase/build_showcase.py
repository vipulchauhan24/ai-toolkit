#!/usr/bin/env python3
"""Keeps the showcase in step with the kit, tests it in a browser, and makes contact sheets.

    python3 -I showcase/build_showcase.py            check the manifest, themes, fonts and sheets
    python3 -I showcase/build_showcase.py --write    rewrite manifest.json by scanning the kit
    python3 -I showcase/build_showcase.py --verify   load every item and report errors
    python3 -I showcase/build_showcase.py --verify --full    every theme, mode and width
    python3 -I showcase/build_showcase.py --sheets   rewrite the kit's contact sheets

Other options: --manifest FILE  --headed  --theme ID --mode M --width N --out DIR  --cli "playwright-cli"
Output lines start with OK, FAIL or RESULT. Exit codes: 0 pass, 1 a FAIL, 2 usage error.
"""
from __future__ import annotations

import argparse
import base64
import functools
import hashlib
import http.server
import json
import os
import shlex
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from urllib.parse import urlencode

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
KIT = ROOT / "skills" / "ui-craft" / "assets" / "kit"
DATA = ROOT / "skills" / "design-md" / "assets" / "data"
SHEETS = KIT / "sheets"
PAGE_CHECKS = ROOT / "skills" / "visual-qa" / "scripts" / "page_checks.js"
WIDTHS = {390: 844, 768: 1024, 1024: 768, 1440: 900, 1920: 1080}
# A lone component or section has no h1, and need not span the page or fill it.
NOT_APPLICABLE = {"h1", "heading-order", "empty-band", "margins"}


def title(name):
    return name.replace("-", " ").capitalize()


def scan():
    items = []
    def add(path, group, name, section=None):
        entry = {"id": path.relative_to(base).with_suffix("").as_posix(), "group": group, "title": name, "file": path.relative_to(ROOT).as_posix()}
        if section:
            entry["section"] = section
        items.append(entry)
    base = KIT
    for path in sorted(KIT.glob("layouts/*/*.html")):
        add(path, "Page", title(path.parent.name))
    for path in sorted(KIT.glob("sections/hero/*.html")):
        add(path, "Heroes", title(path.stem), "hero")
    for folder in sorted(p for p in (KIT / "sections").iterdir() if p.is_dir() and p.name != "hero"):
        for path in sorted(folder.glob("*.html")):
            add(path, title(folder.name), title(path.stem), folder.name)
    for path in sorted(KIT.glob("components/*/*.html")):
        add(path, "Components", title(path.parent.name))
    for path in sorted(KIT.glob("effects/*.html")):
        add(path, "Effects", title(path.stem))
    base = HERE
    for path in sorted((HERE / "signature-examples").glob("*.html")):
        add(path, "Signature examples (not for copying)", title(path.stem))
    return items


def section_hash(section):
    digest = hashlib.sha256()
    for path in sorted((KIT / "sections" / section).iterdir()):
        digest.update(path.name.encode() + path.read_bytes())
    return digest.hexdigest()[:16]


def check(manifest_path, fails):
    try:
        listed = json.loads(manifest_path.read_text(encoding="utf-8"))["items"]
    except (OSError, ValueError, KeyError) as error:
        fails.append("cannot read the manifest: %s" % error)
        return
    found = {i["id"] for i in scan()}
    known = {i["id"] for i in listed}
    fails += ["kit item has no manifest entry: %s" % i for i in sorted(found - known)]
    fails += ["manifest entry has no kit item: %s" % i for i in sorted(known - found)]
    themes = json.loads((HERE / "themes.json").read_text(encoding="utf-8"))["themes"]
    palettes = {p["id"] for p in json.loads((DATA / "palettes.json").read_text(encoding="utf-8"))["palettes"]}
    fonts = {f["id"]: f for f in json.loads((DATA / "fonts.json").read_text(encoding="utf-8"))["pairings"]}
    for theme in themes:
        if theme["palette"] not in palettes:
            fails.append("theme %s: no palette %s" % (theme["id"], theme["palette"]))
        if theme["fonts"] not in fonts:
            fails.append("theme %s: no font pairing %s" % (theme["id"], theme["fonts"]))
            continue
        for package in fonts[theme["fonts"]]["packages"]:
            name = package.split("/")[-1] + "-latin-wght-normal.woff2"
            if not (HERE / "fonts" / name).is_file():
                fails.append("theme %s: font file missing: %s" % (theme["id"], name))
    index = SHEETS / "index.json"
    recorded = json.loads(index.read_text(encoding="utf-8")) if index.is_file() else {}
    for section in sorted({i["section"] for i in scan() if "section" in i}):
        if not (SHEETS / (section + ".jpg")).is_file():
            fails.append("no contact sheet for %s: run --sheets" % section)
        elif recorded.get(section) != section_hash(section):
            fails.append("contact sheet for %s is out of date: run --sheets" % section)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


class Browser:
    def __init__(self, cli, headed):
        self.dir = tempfile.TemporaryDirectory(prefix="showcase-")
        self.work = Path(self.dir.name)
        (self.work / ".playwright").mkdir()
        (self.work / ".playwright" / "cli.config.json").write_text('{"browser":{"browserName":"chromium"}}\n', encoding="utf-8")
        self.cli = shlex.split(cli) + ["-s=showcase-%d" % os.getpid()]
        self.headed = headed
        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.base = "http://127.0.0.1:%d/showcase/" % self.server.server_address[1]
        self.opened = False

    def call(self, *words, timeout=1200):
        return subprocess.run(self.cli + list(words), cwd=str(self.work), capture_output=True, text=True, timeout=timeout)

    def __enter__(self):
        done = self.call("open", "about:blank", *(["--headed"] if self.headed else []), timeout=120)
        if done.returncode != 0:
            raise RuntimeError((done.stderr or done.stdout)[:300])
        self.opened = True
        return self

    def __exit__(self, *exc):
        if self.opened:
            self.call("close", timeout=30)
        self.server.shutdown()
        self.server.server_close()
        self.dir.cleanup()

    def run(self, body):
        script = self.work / "step.js"
        script.write_text(body, encoding="utf-8")
        done = self.call("--raw", "run-code", "--filename=" + str(script))
        if done.returncode != 0:
            raise RuntimeError((done.stderr or done.stdout)[:400])
        return json.loads(done.stdout)


VERIFY_JS = """async page => {
const JOBS = %s;
const PAGE_CHECKS = %s;
let now = null;
page.on("console", (m) => { if (now && m.type() === "error" && !/favicon/.test(m.text())) now.console.push(m.text().slice(0, 200)); });
page.on("pageerror", (e) => { if (now) now.console.push(String(e).slice(0, 200)); });
page.on("response", (r) => { if (now && r.status() >= 400 && !/favicon/.test(r.url())) now.console.push(r.status() + " " + r.url()); });
const cdp = await page.context().newCDPSession(page);
const out = [];
for (const job of JOBS) {
  now = { job: job.label, console: [], findings: [] };
  await cdp.send("Emulation.setTouchEmulationEnabled", { enabled: job.width <= 820 });
  await page.setViewportSize({ width: job.width, height: job.height });
  try {
    await page.goto(job.url, { waitUntil: "load" });
    await page.waitForFunction(() => document.documentElement.hasAttribute("data-showcase-ready"), null, { timeout: 8000 });
    if (job.scroll) {
      await page.evaluate(async () => {
        for (let y = 0; y < document.documentElement.scrollHeight; y += 400) { window.scrollTo({ top: y, behavior: "instant" }); await new Promise((r) => setTimeout(r, 60)); }
      });
      await page.waitForTimeout(700);
    }
    now.findings = (await page.evaluate(PAGE_CHECKS)).findings.filter((f) => f.severity === "fail");
  } catch (e) { now.console.push("did not render: " + String(e).slice(0, 160)); }
  out.push(now);
  now = null;
}
return out;
}
"""

SHEET_JS = """async page => {
const CONFIG = %s;
const out = {};
const cdp = await page.context().newCDPSession(page);
await page.setViewportSize({ width: 1000, height: 900 });
for (const [section, url] of Object.entries(CONFIG)) {
  await page.goto(url, { waitUntil: "load" });
  await page.waitForFunction(() => document.documentElement.hasAttribute("data-showcase-ready"), null, { timeout: 30000 });
  const box = await page.evaluate(() => { const r = document.querySelector("main").getBoundingClientRect(); return { width: Math.ceil(r.width), height: Math.ceil(r.height) }; });
  const shot = await cdp.send("Page.captureScreenshot", { format: "jpeg", quality: 62, captureBeyondViewport: true, clip: { x: 0, y: 0, width: box.width, height: box.height, scale: 1 } });
  out[section] = shot.data;
}
return out;
}
"""


def render_url(base, item, **params):
    return base + "render.html?" + urlencode(dict(item=item["id"], **params))


def verify(args, items, fails):
    themes = [t["id"] for t in json.loads((HERE / "themes.json").read_text(encoding="utf-8"))["themes"]]
    checks = PAGE_CHECKS.read_text(encoding="utf-8").strip()
    with Browser(args.cli, args.headed) as browser:
        batches = []
        motion = [dict(url=render_url(browser.base, i, theme=themes[0]), width=1440, height=900, scroll=True, label="%s motion on" % i["id"]) for i in items]
        long_text = [dict(url=render_url(browser.base, i, theme=themes[0], content="long", reduced=1), width=390, height=844, scroll=False, label="%s long content 390" % i["id"]) for i in items]
        batches.append(motion + long_text)
        if args.full:
            for theme in themes:
                for mode in ("light", "dark"):
                    batches.append([dict(url=render_url(browser.base, i, theme=theme, mode=mode, reduced=1), width=w, height=h, scroll=False, label="%s %s %s %d" % (i["id"], theme, mode, w))
                                    for i in items for w, h in WIDTHS.items()])
        total = 0
        seen = {}
        for jobs in batches:
            total += len(jobs)
            for result in browser.run(VERIFY_JS % (json.dumps(jobs), checks)):
                item, _, where = result["job"].partition(" ")
                for line in result["console"]:
                    seen.setdefault((item, "console", line), []).append(where)
                for f in result["findings"]:
                    if f["id"] not in NOT_APPLICABLE:
                        seen.setdefault((item, f["id"], "; ".join(f["samples"]) or f["message"]), []).append(where)
    for (item, kind, detail), wheres in sorted(seen.items()):
        fails.append("%s: %s: %s (%d view(s), first: %s)" % (item, kind, detail[:150], len(wheres), wheres[0]))
    print("OK   %d views rendered" % total)


def sheets(args, items, fails):
    out = Path(args.out) if args.out else SHEETS
    out.mkdir(parents=True, exist_ok=True)
    sections = sorted({i["section"] for i in items if "section" in i})
    with Browser(args.cli, args.headed) as browser:
        query = {"theme": args.theme, "mode": args.mode or "light", "width": args.width}
        config = {s: browser.base + "sheet.html?" + urlencode(dict(query, section=s)) for s in sections}
        for section, data in browser.run(SHEET_JS % json.dumps(config)).items():
            (out / (section + ".jpg")).write_bytes(base64.b64decode(data))
            print("OK   %s.jpg" % section)
    if not args.out:
        (out / "index.json").write_text(json.dumps({s: section_hash(s) for s in sections}, indent=2) + "\n", encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Showcase manifest, browser test and contact sheets.")
    ap.add_argument("--manifest", default=str(HERE / "manifest.json"))
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--full", action="store_true", help="with --verify: every theme, mode and width")
    ap.add_argument("--only", help="with --verify: items whose id contains this text")
    ap.add_argument("--sheets", action="store_true")
    ap.add_argument("--theme", default="cool")
    ap.add_argument("--mode", default="")
    ap.add_argument("--width", default="1280")
    ap.add_argument("--out", help="with --sheets: write here and leave the kit's sheets alone")
    ap.add_argument("--headed", action="store_true")
    ap.add_argument("--cli", default=os.environ.get("SHOWCASE_CLI", "playwright-cli"))
    args = ap.parse_args(argv)
    manifest = Path(args.manifest)
    fails = []
    if args.write:
        manifest.write_text(json.dumps({"items": scan()}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("OK   wrote %s" % manifest)
    items = [i for i in scan() if not args.only or args.only in i["id"]]
    try:
        if args.sheets:
            sheets(args, items, fails)
        if args.verify:
            verify(args, items, fails)
    except (RuntimeError, ValueError, subprocess.TimeoutExpired) as error:
        fails.append("browser step failed: %s" % str(error)[:400])
    if not (args.verify or args.sheets) or args.write:
        check(manifest, fails)
    for line in fails:
        print("FAIL " + line)
    print("RESULT  %s" % ("FAIL" if fails else "PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
