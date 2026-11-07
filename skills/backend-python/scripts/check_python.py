#!/usr/bin/env python3
"""Check Python files written by the backend-python skill.

Usage:  python3 -I check_python.py [--django] [--fastapi] FILE [FILE ...]

--django adds checks for a Django project. --fastapi adds checks for a FastAPI
project. Both flags may be given together. Only .py files are checked; others
print SKIP. Exit 0 when no FAIL line printed, 1 when any did, 2 (this text) when
no file is given or a flag is unknown.

Static, line-level checks on comment-stripped text (P9 and the type-ignore,
TODO and PLACEHOLDER-DATA reports use the raw text). They complement the
project's own typecheck and lint, which are more precise; run those first.
Limits: line-level only; a multi-line `def` signature is not checked by P10;
multi-line SQL strings are missed.

  FAIL    P1   bare `except:`
          P2   `except ...:` whose body is only `pass`
          P3   `print(`
          P4   a `def` parameter defaulting to `[]`, `{}` or `set()`
          P5   `eval(` or `exec(`
          P6   `from x import *`
          P7   a name with password, secret, api_key or token assigned a string
               literal of 8 or more characters
          P8   a string starting with an SQL statement, or `.raw(`, `.extra(`,
               `cursor.execute(`
          P9   `# type: ignore` with no bracketed error code
          P10  a single-line public `def` with no `->`
  --django
          D1   HttpResponse, JsonResponse, `render(`, or a function whose first
               parameter is `request`
          D2   `DEBUG = True`
          D3   `SECRET_KEY` assigned a string literal
  --fastapi
          F1   `@app.` or `@router.` followed by get, post, put, patch, delete
               or api_route
  REPORT  `os.environ` in a file not named like settings or config, `global `,
          TODO, `# type: ignore[code]`, PLACEHOLDER-DATA
"""
import re
import sys
from pathlib import Path

PY = {".py"}
LINE_COMMENT = re.compile(r"(^|\s)#.*$")

# (id, compiled regex, message). Matched against comment-stripped text.
CHECKS = [
    ("P1", re.compile(r"^[ \t]*except[ \t]*:", re.M), "bare except: catch a specific exception"),
    ("P2", re.compile(r"^[ \t]*except\b[^\n]*:[ \t]*(?:\n[ \t]*)?pass[ \t]*$", re.M),
     "swallowed exception: handle it or re-raise"),
    ("P3", re.compile(r"(?<![\w.])print\("), "print left in: use the logging module"),
    ("P4", re.compile(r"\bdef[ \t]+\w+[ \t]*\([^)]*=[ \t]*(?:\[\]|\{\}|set\(\))"),
     "mutable default argument: default to None"),
    ("P5", re.compile(r"(?<![\w.])(?:eval|exec)\("), "dynamic code execution: remove it"),
    ("P6", re.compile(r"^[ \t]*from[ \t]+[\w.]+[ \t]+import[ \t]+\*", re.M),
     "star import: import names explicitly"),
    ("P7", re.compile(r"""\b\w*(?:password|secret|api_key|token)\w*[ \t]*(?::[^=\n]+)?(?<![=!<>])=(?!=)[ \t]*(["'])[^"'\n]{8,}\1""", re.I),
     "hard-coded secret: read it from configuration"),
    ("P8", re.compile(r"""["']\s*(?:select\s[^"'\n]*\sfrom\b|insert\s+into\b|update\s[^"'\n]*\sset\b|delete\s+from\b)""", re.I),
     "SQL in service code: queries belong to db-query-migration"),
    ("P8", re.compile(r"\.(?:raw|extra)\(|\bcursor\.execute\("),
     "SQL in service code: queries belong to db-query-migration"),
    ("P10", re.compile(r"^[ \t]*(?:async[ \t]+)?def[ \t]+(?![_]|test_)\w+(?![^\n]*->)[ \t]*\([^\n]*\)[ \t]*:", re.M),
     "public function without a return annotation"),
]

# Matched against the raw text (the rule needs the comment).
RAW_CHECKS = [
    ("P9", re.compile(r"#[ \t]*type:[ \t]*ignore(?!\[)"), "type: ignore without a code: name the error"),
]

DJANGO_CHECKS = [
    ("D1", re.compile(r"\b(?:HttpResponse|JsonResponse)\b|(?<![\w.])render\(|\bdef[ \t]+\w+[ \t]*\([ \t]*(?:self[ \t]*,[ \t]*)?request\b"),
     "view code: views belong to api-builder"),
    ("D2", re.compile(r"^[ \t]*DEBUG[ \t]*=[ \t]*True\b", re.M), "DEBUG on: read it from the environment, default False"),
    ("D3", re.compile(r"""^[ \t]*SECRET_KEY[ \t]*=[ \t]*["']""", re.M), "SECRET_KEY in source: read it from the environment"),
]

FASTAPI_CHECKS = [
    ("F1", re.compile(r"^[ \t]*@(?:app|router)\.(?:get|post|put|patch|delete|api_route)\b", re.M),
     "route handler: handlers belong to api-builder"),
]

# Each match is a REPORT line. (regex, message, uses_raw_text)
REPORT_CHECKS = [
    (re.compile(r"\bglobal[ \t]+\w"), "global statement: pass the value instead", False),
    (re.compile(r"\bTODO\b"), "TODO: list it in the report", True),
    (re.compile(r"#[ \t]*type:[ \t]*ignore\["), "type: ignore with a code: list it in the report", True),
    (re.compile(r"PLACEHOLDER-DATA"), "PLACEHOLDER-DATA: list it in the report", True),
]
ENVIRON = re.compile(r"\bos\.environ\b")

FLAGS = {"--django": DJANGO_CHECKS, "--fastapi": FASTAPI_CHECKS}


def strip_comments(text):
    """Blank out comments but keep line breaks, so line numbers stay right."""
    return "\n".join(LINE_COMMENT.sub(r"\1", ln) for ln in text.split("\n"))


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def check_file(path, flags=()):
    fails, reports = [], []
    raw = path.read_text(encoding="utf-8", errors="replace")
    text = strip_comments(raw)

    rules = list(CHECKS)
    for flag in flags:
        rules += FLAGS[flag]
    for _id, rx, msg in rules:
        for m in rx.finditer(text):
            fails.append((line_of(text, m.start()), msg))
    for _id, rx, msg in RAW_CHECKS:
        for m in rx.finditer(raw):
            fails.append((line_of(raw, m.start()), msg))

    for rx, msg, use_raw in REPORT_CHECKS:
        src = raw if use_raw else text
        for m in rx.finditer(src):
            reports.append((line_of(src, m.start()), msg))
    stem = path.stem.lower()
    if "settings" not in stem and "config" not in stem:
        for m in ENVIRON.finditer(text):
            reports.append((line_of(text, m.start()),
                            "os.environ outside a settings or config module: read the environment in one place"))

    return sorted(set(fails)), sorted(set(reports))


def main(argv):
    flags = [a for a in argv if a.startswith("--")]
    files = [Path(a) for a in argv if not a.startswith("--")]
    if not files or any(f not in FLAGS for f in flags):
        print(__doc__)
        return 2
    failed = False
    for p in sorted(files, key=str):
        if not p.is_file():
            print(f"SKIP    {p}: not a file")
            continue
        if p.suffix not in PY:
            print(f"SKIP    {p}: not a .py file")
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
