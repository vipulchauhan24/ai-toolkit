#!/usr/bin/env python3
"""Stands in for playwright-cli so preview.py can be tested with no browser.

It logs each call to cli.log in the working directory. Set FAKE_CLI_FAIL=open to fail that step.
"""
import os
import sys
from pathlib import Path


def main():
    args = sys.argv[1:]
    with open("cli.log", "a", encoding="utf-8") as log:
        log.write(" ".join(args) + "\n")
    words = [a for a in args if not a.startswith("-s=")]
    if os.environ.get("FAKE_CLI_FAIL") == words[0]:
        print("the browser could not start", file=sys.stderr)
        return 1
    if words[0] == "screenshot":
        Path(words[1][len("--filename="):]).write_bytes(b"png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
