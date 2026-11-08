#!/usr/bin/env python3
"""Screenshots each concept preview at desktop and phone width. Standard library only.

Usage:

    python3 -I preview.py --dir previews --names a,b,c

It serves the folder on 127.0.0.1 for the length of the run, opens a visible browser with
Playwright CLI, and saves <dir>/shots/<name>-1440.png and <name>-390.png.

Options: --headless  --cli "playwright-cli"
Output lines start with OK, FAIL or RESULT. Exit codes: 0 done, 1 failed, 2 usage error.
"""
from __future__ import annotations

import argparse
import functools
import http.server
import os
import re
import shlex
import subprocess
import sys
import threading
from pathlib import Path

SIZES = [(1440, 900), (390, 844)]
TIMEOUT = 120


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class Stop(Exception):
    pass


def main(argv=None):
    ap = argparse.ArgumentParser(description="Screenshots concept previews.")
    ap.add_argument("--dir", required=True, help="folder holding <name>.html files")
    ap.add_argument("--names", required=True, help="comma-separated names, such as a,b,c")
    ap.add_argument("--headless", action="store_true", help="no visible window")
    ap.add_argument("--cli", default=os.environ.get("UI_CRAFT_CLI", "playwright-cli"))
    args = ap.parse_args(argv)
    root = Path(args.dir).resolve()
    names = [n.strip() for n in args.names.split(",") if n.strip()]
    if not names or not all(re.fullmatch(r"[\w-]+", n) for n in names):
        print("usage error: --names is a comma-separated list of plain names", file=sys.stderr)
        return 2
    missing = [n for n in names if not (root / (n + ".html")).is_file()]
    if missing:
        print("usage error: no such preview in %s: %s" % (root, ", ".join(missing)), file=sys.stderr)
        return 2

    shots = root / "shots"
    work = shots / ".browser"
    (work / ".playwright").mkdir(parents=True, exist_ok=True)
    (work / ".playwright" / "cli.config.json").write_text('{"browser":{"browserName":"chromium"}}\n', encoding="utf-8")
    cli = shlex.split(args.cli) + ["-s=ui-craft-preview-%d" % os.getpid()]

    def call(*words):
        try:
            done = subprocess.run(cli + list(words), cwd=str(work), capture_output=True, text=True, timeout=TIMEOUT)
        except FileNotFoundError:
            raise Stop("%s is not installed" % cli[0])
        except subprocess.TimeoutExpired:
            raise Stop("%s timed out" % words[0])
        if done.returncode != 0 or "### Error" in done.stdout:
            raise Stop("%s failed: %s" % (words[0], (done.stderr or done.stdout).strip()[:300]))

    handler = functools.partial(QuietHandler, directory=str(root))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d/" % server.server_address[1]
    opened = False
    try:
        call("open", "about:blank", *([] if args.headless else ["--headed"]))
        opened = True
        for name in names:
            for width, height in SIZES:
                call("resize", str(width), str(height))
                call("goto", base + name + ".html")
                target = shots / ("%s-%d.png" % (name, width))
                call("screenshot", "--filename=" + str(target))
                print("OK   %s" % target)
    except Stop as stop:
        print("FAIL %s" % stop)
        print("RESULT  FAIL")
        return 1
    finally:
        if opened:
            try:
                call("close")
            except Stop:
                pass
        server.shutdown()
        server.server_close()
    print("RESULT  PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
