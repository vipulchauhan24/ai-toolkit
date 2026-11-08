#!/usr/bin/env python3
"""Drives a visible browser through a site and saves what it finds. Standard library only.

Every browser step is a `playwright-cli` call, so the user can watch the window. The
script writes results.json, tiles/ (images sized for grading), full/ (full-page PNGs)
and extra/ into the output folder. Grading and the report come after it.

Usage:

    python3 -I capture.py --url http://localhost:3000 --out .qa/20261108-0730

Options: --routes /,/about  --max-routes 10  --viewports 390x844,1440x900  --themes light,dark
         --no-interact  --no-reduced  --allow-remote  --headless  --cli "playwright-cli"

Output lines start with OK, WARN, FAIL or RESULT. Exit codes: 0 done, 1 failed, 2 usage error.
"""
from __future__ import annotations

import argparse
import base64
import datetime
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

HERE = Path(__file__).resolve().parent
DEFAULT_VIEWPORTS = "390x844,768x1024,1024x768,1440x900,1920x1080"
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}
GRADE_WIDTH = 1000
TILE_HEIGHT = 1500
MAX_TILES = 8
MAX_LINKS = 25
STEP_TIMEOUT = 240


class Stop(Exception):
    """The run cannot continue."""


class Browser:
    def __init__(self, cli, out, headless):
        self.cli = cli
        self.out = out
        self.headless = headless
        self.session = "-s=visual-qa-%d" % os.getpid()
        self.opened = False
        self.step_file = out / ".step.js"
        self.source = (HERE / "steps.js").read_text(encoding="utf-8")
        self.checks = (HERE / "page_checks.js").read_text(encoding="utf-8")

    def call(self, *args, raw=False, timeout=STEP_TIMEOUT):
        cmd = self.cli + ([self.session] if not args[0].startswith("--") else [])
        cmd += (["--raw"] if raw else []) + list(args)
        try:
            done = subprocess.run(cmd, cwd=str(self.out), capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return 1, "", "timed out after %d seconds" % timeout
        except FileNotFoundError:
            return 127, "", "%s is not installed" % self.cli[0]
        return done.returncode, done.stdout, done.stderr

    def open(self):
        (self.out / ".playwright").mkdir(exist_ok=True)
        (self.out / ".playwright" / "cli.config.json").write_text('{"browser":{"browserName":"chromium"}}\n', encoding="utf-8")
        args = ["open", "about:blank"] + ([] if self.headless else ["--headed"])
        rc, out, err = self.call(*args)
        if rc != 0 or "Error" in out[:400]:
            raise Stop("the browser did not open: " + (err or out).strip()[:400])
        self.opened = True

    def close(self):
        if self.opened:
            self.call("close", timeout=30)
            self.opened = False

    def step(self, **config):
        body = "async page => {\nconst CONFIG = %s;\nconst PAGE_CHECKS = %s;\n%s\n}\n" % (json.dumps(config), self.checks.strip(), self.source)
        self.step_file.write_text(body, encoding="utf-8")
        rc, out, err = self.call("run-code", "--filename=" + str(self.step_file), raw=True)
        if rc != 0:
            raise RuntimeError((err or out).strip()[:400])
        try:
            return json.loads(out)
        except ValueError:
            raise RuntimeError(out.strip()[:400] or "the step returned nothing")


def slug(route):
    name = re.sub(r"[^a-z0-9]+", "-", route.lower()).strip("-")
    return name or "home"


def viewports(text):
    out = []
    for item in text.split(","):
        m = re.fullmatch(r"(\d{3,4})x(\d{3,4})", item.strip())
        if not m:
            raise ValueError("bad viewport %r: use WIDTHxHEIGHT" % item)
        out.append((int(m.group(1)), int(m.group(2))))
    return out


def save_image(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64decode(data))


def merge_findings(findings):
    """One entry per check and severity, however many elements or keyboard stops tripped it."""
    merged = {}
    for f in findings:
        key = (f["id"], f["severity"])
        if key not in merged:
            merged[key] = dict(f, samples=list(f["samples"]))
            continue
        kept = merged[key]
        kept["count"] += f["count"]
        kept["samples"] += [s for s in f["samples"] if s not in kept["samples"]]
        kept["samples"] = kept["samples"][:3]
    return list(merged.values())


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def relative(path, out):
    return path.relative_to(out).as_posix()


def build_parser():
    ap = argparse.ArgumentParser(description="Visible-browser capture for the visual-qa skill.")
    ap.add_argument("--url", required=True, help="base URL of the running site")
    ap.add_argument("--out", required=True, help="new folder for this run")
    ap.add_argument("--routes", default="", help="comma-separated paths; default: found from the links on the base page")
    ap.add_argument("--max-routes", type=int, default=10)
    ap.add_argument("--viewports", default=DEFAULT_VIEWPORTS)
    ap.add_argument("--themes", default="light,dark")
    ap.add_argument("--no-interact", action="store_true", help="skip keyboard, link, form and menu checks")
    ap.add_argument("--no-reduced", action="store_true", help="skip the reduced-motion pass")
    ap.add_argument("--allow-remote", action="store_true", help="click links and submit forms on a host that is not local")
    ap.add_argument("--headless", action="store_true", help="no visible window; only when the user asks")
    ap.add_argument("--scroll-pause", type=int, default=180, help="milliseconds between scroll steps")
    ap.add_argument("--cli", default=os.environ.get("VISUAL_QA_CLI", "playwright-cli"), help="command that runs Playwright CLI")
    return ap


def run(args, out):
    views = viewports(args.viewports)
    themes = [t.strip() for t in args.themes.split(",") if t.strip()]
    if not themes or set(themes) - {"light", "dark"}:
        raise ValueError("themes must be light, dark or both")
    if not re.match(r"https?://", args.url):
        raise ValueError("--url must start with http:// or https://")
    base = args.url if args.url.endswith("/") else args.url + "/"
    host = urlparse(base).hostname or ""
    local = host in LOCAL_HOSTS
    interact_on = not args.no_interact and (local or args.allow_remote)

    browser = Browser(shlex.split(args.cli), out, args.headless)
    rc, version, err = browser.call("--version", timeout=60)
    if rc != 0:
        raise Stop("Playwright CLI is not available (%s). Install it with: npm install -g @playwright/cli@latest" % (err or version).strip()[:200])

    results = {
        "run": {"url": base, "started": now(), "ended": None, "cli_version": version.strip(), "viewports": ["%dx%d" % v for v in views],
                "themes": themes, "headed": not args.headless, "local": local, "interactions": interact_on, "reduced_motion": not args.no_reduced},
        "routes": [], "skipped_routes": [], "shots": [], "site_findings": [], "route_findings": {}, "external_links": [], "extras": [], "errors": [], "notes": [],
    }
    if not local and not interact_on and not args.no_interact:
        results["notes"].append("Links and forms were not exercised because this is not a local site.")

    def error(where, exc):
        results["errors"].append("%s: %s" % (where, exc))
        print("FAIL %s: %s" % (where, exc))

    try:
        browser.open()
        print("OK   browser open (%s)" % ("headless" if args.headless else "visible window"))
        if args.routes:
            routes = [r.strip() for r in args.routes.split(",") if r.strip()]
        else:
            routes = browser.step(step="discover", base=base)["routes"]
        results["skipped_routes"] = routes[args.max_routes:]
        routes = routes[: args.max_routes]
        results["routes"] = routes
        print("OK   %d route(s): %s" % (len(routes), ", ".join(routes)))
        if results["skipped_routes"]:
            print("WARN %d route(s) over the limit were skipped" % len(results["skipped_routes"]))

        total = len(routes) * len(views) * len(themes)
        count = 0
        no_dark = []
        for route in routes:
            url = urljoin(base, route.lstrip("/"))
            for width, height in views:
                light_bg = None
                for theme in themes:
                    count += 1
                    sid = "%s-%d-%s" % (slug(route), width, theme)
                    try:
                        data = browser.step(step="shot", url=url, width=width, height=height, theme=theme, lightBackground=light_bg,
                                            gradeWidth=GRADE_WIDTH, tileHeight=TILE_HEIGHT, maxTiles=MAX_TILES, scrollPause=args.scroll_pause)
                    except RuntimeError as exc:
                        error(sid, exc)
                        continue
                    if theme == "light":
                        light_bg = data["checks"]["background"]
                    if data["themeVia"] == "none":
                        if route not in no_dark:
                            no_dark.append(route)
                        print("WARN %s: the site has no dark theme; shot dropped" % sid)
                        continue
                    tiles = []
                    for i, image in enumerate(data["tiles"], 1):
                        path = out / "tiles" / ("%s-%02d.jpg" % (sid, i))
                        save_image(path, image)
                        tiles.append(relative(path, out))
                    full = out / "full" / (sid + ".png")
                    full.parent.mkdir(exist_ok=True)
                    rc, cli_out, cli_err = browser.call("screenshot", "--full-page", "--filename=" + str(full))
                    if rc != 0 or not full.exists():
                        error(sid + " full-page screenshot", (cli_err or cli_out).strip()[:200])
                    results["shots"].append({
                        "id": sid, "route": route, "viewport": [width, height], "theme": theme, "title": data["checks"]["title"],
                        "page_height": data["checks"]["pageHeight"], "tiles": tiles, "full": relative(full, out) if full.exists() else None,
                        "truncated": data["truncated"], "theme_via": data["themeVia"], "findings": data["checks"]["findings"],
                        "console": data["console"], "failed_requests": data["failed"],
                    })
                    fails = sum(1 for f in data["checks"]["findings"] if f["severity"] == "fail")
                    print("OK   %d/%d %s: %d tile(s), %d failing check(s)" % (count, total, sid, len(tiles), fails))
        if no_dark:
            results["notes"].append("No dark theme and no theme button on: %s. Its dark shots were dropped." % ", ".join(no_dark))

        seen = []
        for route in routes:
            url = urljoin(base, route.lstrip("/"))
            findings = []
            if not args.no_reduced:
                try:
                    findings += browser.step(step="reduced", url=url, width=1440, height=900)["findings"]
                    print("OK   reduced motion checked: " + route)
                except RuntimeError as exc:
                    error("reduced motion on " + route, exc)
            if interact_on:
                try:
                    data = browser.step(step="interact", url=url, seen=seen, maxLinks=MAX_LINKS)
                except RuntimeError as exc:
                    error("interactions on " + route, exc)
                else:
                    findings += data["findings"]
                    seen += data["checked"]
                    results["external_links"] = sorted(set(results["external_links"]) | set(data["external"]))
                    if data.get("menu"):
                        path = out / "extra" / ("%s-menu-390.jpg" % slug(route))
                        save_image(path, data["menu"])
                        results["extras"].append({"route": route, "label": "Phone menu open", "image": relative(path, out)})
                    print("OK   interactions checked: %s (%d keyboard stops, %d links)" % (route, data["stops"], len(data["checked"])))
            results["route_findings"][route] = merge_findings(findings)
    finally:
        browser.close()
        step_file = out / ".step.js"
        if step_file.exists():
            step_file.unlink()

    results["run"]["ended"] = now()
    (out / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print("OK   wrote %s" % (out / "results.json"))
    if not results["shots"]:
        print("FAIL no screenshot was captured")
        return 1
    return 1 if results["errors"] else 0


def main(argv=None):
    args = build_parser().parse_args(argv)
    out = Path(args.out).resolve()
    if out.exists() and any(out.iterdir()):
        print("FAIL %s already has files: use a new folder" % out)
        print("RESULT  FAIL")
        return 1
    out.mkdir(parents=True, exist_ok=True)
    try:
        code = run(args, out)
    except ValueError as exc:
        print("usage error: %s" % exc, file=sys.stderr)
        return 2
    except (Stop, RuntimeError) as exc:
        print("FAIL %s" % exc)
        code = 1
    print("RESULT  %s" % ("PASS" if code == 0 else "FAIL"))
    return code


if __name__ == "__main__":
    sys.exit(main())
