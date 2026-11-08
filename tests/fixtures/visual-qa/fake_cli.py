#!/usr/bin/env python3
"""Stands in for playwright-cli so capture.py can be tested with no browser.

It answers each call the way the real CLI does and appends the arguments to cli.log in
the working directory. The /about route has no dark theme, and the /broken route fails.
"""
import base64
import json
import re
import sys
from pathlib import Path

PIXEL = base64.b64encode(b"\xff\xd8\xff\xd9").decode("ascii")


def answer(config):
    step = config["step"]
    if step == "discover":
        return {"routes": ["/", "/about", "/broken"]}
    if step == "shot":
        if "/broken" in config["url"]:
            return None
        checks = {"findings": [{"id": "margins", "severity": "fail", "message": "Uneven side margins", "count": 1, "samples": []}],
                  "pageHeight": 2000, "title": "Fake", "background": "rgb(255, 255, 255)"}
        via = "none" if config["theme"] == "dark" and "/about" in config["url"] else "preference"
        return {"checks": checks, "tiles": [PIXEL, PIXEL], "truncated": False, "themeVia": via, "console": [], "failed": []}
    if step == "reduced":
        return {"findings": []}
    if step == "interact":
        repeat = {"id": "focus-visible", "severity": "fail", "message": "No ring", "count": 1, "samples": ["a"]}
        return {"findings": [repeat, dict(repeat, samples=["b"])], "checked": ["http://localhost/x"], "external": ["https://example.com/"], "stops": 2, "menu": PIXEL}
    raise SystemExit("unknown step " + step)


def main():
    args = sys.argv[1:]
    with open("cli.log", "a", encoding="utf-8") as log:
        log.write(" ".join(args) + "\n")
    if args[0] == "--version":
        print("0.0.0-fake")
        return 0
    words = [a for a in args if not a.startswith("-s=") and a != "--raw"]
    command = words[0]
    if command in ("open", "close"):
        print("### done")
        return 0
    if command == "screenshot":
        Path(next(a for a in words if a.startswith("--filename="))[len("--filename="):]).write_bytes(b"png")
        return 0
    if command == "run-code":
        source = Path(next(a for a in words if a.startswith("--filename="))[len("--filename="):]).read_text(encoding="utf-8")
        config = json.loads(re.search(r"const CONFIG = (.*);\n", source).group(1))
        result = answer(config)
        if result is None:
            print("### Error\nthe page crashed", file=sys.stderr)
            return 1
        print(json.dumps(result))
        return 0
    raise SystemExit("unknown command " + command)


if __name__ == "__main__":
    sys.exit(main())
