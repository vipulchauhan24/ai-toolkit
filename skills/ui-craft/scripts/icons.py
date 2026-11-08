#!/usr/bin/env python3
"""Copies the Tabler icons a project uses into a folder. Standard library only.

Usage:

    python3 -I icons.py --out public/icons --names arrow-right,brand-github
    python3 -I icons.py --out public/icons src/index.html      (finds data-icon="name")

A name Tabler does not have is printed as MISSING: write it as text and never draw it.
Output lines start with OK, MISSING, FAIL or RESULT. Exit codes: 0 done, 1 failed, 2 usage error.
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/tabler/tabler-icons/v3.50.0/icons/outline"
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Copies Tabler icons into a project.")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--out", required=True)
    ap.add_argument("--names", default="")
    ap.add_argument("--base", default=BASE, help="where the icons are fetched from")
    args = ap.parse_args(argv)
    names = {n.strip() for n in args.names.split(",") if n.strip()}
    for item in args.files:
        path = Path(item)
        if not path.is_file():
            print("usage error: %s is not a file" % item, file=sys.stderr)
            return 2
        names |= set(re.findall(r'data-icon="([^"]+)"', path.read_text(encoding="utf-8")))
    if not names:
        print("usage error: no icon names given or found", file=sys.stderr)
        return 2
    bad = sorted(n for n in names if not NAME.match(n))
    if bad:
        print("usage error: not an icon name: %s" % ", ".join(bad), file=sys.stderr)
        return 2
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    copied = 0
    for name in sorted(names):
        try:
            with urllib.request.urlopen("%s/%s.svg" % (args.base, name), timeout=20) as reply:
                data = reply.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                print("FAIL %s: HTTP %d" % (name, exc.code))
                print("RESULT  FAIL")
                return 1
            print("MISSING %s: Tabler has no such icon. Write the name as text" % name)
            continue
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, FileNotFoundError):
                print("MISSING %s: Tabler has no such icon. Write the name as text" % name)
                continue
            print("FAIL could not fetch %s: %s" % (name, exc))
            print("RESULT  FAIL")
            return 1
        except OSError as exc:
            print("FAIL could not fetch %s: %s" % (name, exc))
            print("RESULT  FAIL")
            return 1
        svg = re.sub(r"<!--.*?-->", "", data, flags=re.S).strip()
        (out / (name + ".svg")).write_text(svg + "\n", encoding="utf-8")
        copied += 1
    print("OK   %d icon(s) in %s" % (copied, out))
    print("RESULT  PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
