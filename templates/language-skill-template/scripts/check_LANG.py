#!/usr/bin/env python3
"""Check <<LANG>> files written by the <<NAME>> skill.

Usage:  python3 -I check_LANG.py [FRAMEWORK FLAG] FILE [FILE ...]

Static, line-level checks. They complement the project's own typecheck and lint,
which are more precise; run those first. FAIL exits 1.

  FAIL    (none yet: add rules to CHECKS)
  REPORT  PLACEHOLDER-DATA markers
  flags   (none yet: add framework flags to FRAMEWORK_FLAGS)
"""
import re
import sys
from pathlib import Path

LANG_EXT = {".EXT"}
LINE_COMMENT_PREFIX = "#"  # set to the language's line comment, for example "//" or "--"
BLOCK_COMMENT = None  # for example re.compile(r"/\*.*?\*/", re.S); None if the language has none

# (compiled regex, message, extensions). Matched against comment-stripped text.
CHECKS = [
    # (re.compile(r"\bdebug_print\("), "debug output left in: remove it", LANG_EXT),
]

# (compiled regex, message, extensions). Matched against the raw text; each match is a REPORT line.
REPORT_CHECKS = [
    (re.compile(r"PLACEHOLDER-DATA"), "PLACEHOLDER-DATA: list it in the report", LANG_EXT),
]

# Framework flags, for example {"--django": "Django"}. A flag turns on check_framework().
FRAMEWORK_FLAGS = {}

LINE_COMMENT = re.compile(r"(^|\s)" + re.escape(LINE_COMMENT_PREFIX) + r".*$")


def strip_comments(text):
    """Blank out comments but keep line breaks, so line numbers stay right."""
    if BLOCK_COMMENT is not None:
        text = BLOCK_COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    return "\n".join(LINE_COMMENT.sub(r"\1", ln) for ln in text.split("\n"))


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def check_framework(path, raw, text, flags):
    """Framework-specific checks. Return (fails, reports): lists of (line, message)."""
    return [], []


def check_file(path, flags=()):
    fails, reports = [], []
    raw = path.read_text(encoding="utf-8", errors="replace")
    text = strip_comments(raw)
    ext = path.suffix

    for rx, msg, exts in CHECKS:
        if ext in exts:
            for m in rx.finditer(text):
                fails.append((line_of(text, m.start()), msg))

    for rx, msg, exts in REPORT_CHECKS:
        if ext in exts:
            for m in rx.finditer(raw):
                reports.append((line_of(raw, m.start()), msg))

    if flags:
        nf, nr = check_framework(path, raw, text, flags)
        fails += nf
        reports += nr

    return sorted(set(fails)), sorted(set(reports))


def main(argv):
    flags = [a for a in argv if a.startswith("--")]
    files = [Path(a) for a in argv if not a.startswith("--")]
    unknown = [f for f in flags if f not in FRAMEWORK_FLAGS]
    if not files or unknown:
        print(__doc__)
        return 2
    failed = False
    for p in files:
        if not p.is_file():
            print(f"SKIP    {p}: not a file")
            continue
        if p.suffix not in LANG_EXT:
            print(f"SKIP    {p}: not a {'/'.join(sorted(LANG_EXT))} file")
            continue
        fails, reports = check_file(p, flags)
        for ln, msg in fails:
            print(f"FAIL    {p}:{ln}: {msg}")
        for ln, msg in reports:
            print(f"REPORT  {p}:{ln}: {msg}")
        failed = failed or bool(fails)
    print("RESULT  " + ("FAIL" if failed else "PASS"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
