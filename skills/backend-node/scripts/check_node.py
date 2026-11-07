#!/usr/bin/env python3
"""Check Node.js and TypeScript files written by the backend-node skill.

Usage:  python3 -I check_node.py [--express] [--nest] FILE [FILE ...]

--express adds the Express check (E1). --nest adds the NestJS checks (M1, M2).

Static, line-level checks on comment-stripped text. They complement the project's own
typecheck and lint, which are more precise; run those first. FAIL exits 1.
Files accepted: .ts, .tsx, .mts, .cts. Other files print SKIP.

  FAIL    N1  `: any`, `as any`, `<any>`
          N2  @ts-ignore (searched in the raw text, because it only appears in comments)
          N3  console.log(
          N4  eval( or new Function(
          N5  require( in a .ts, .tsx or .mts file
          N6  a name matching password, secret, apikey, api_key or token assigned a string
              literal of 8 or more characters (a line containing `test-only` is skipped)
          N7  a string or template literal starting with an SQL statement
              (select ... from, insert into, update ... set, delete from)
  REPORT  process.env in a file whose name does not contain "config"; non-null assertion
          (`!.` or `!)`); `as unknown as`; TODO; PLACEHOLDER-DATA
  --express  FAIL  E1  app. or router. followed by get, post, put, patch, delete or all and (
  --nest     FAIL  M1  @Controller(, @Get(, @Post(, @Put(, @Patch(, @Delete(, @All(
                   M2  new <Name>Service( or new <Name>Repository(

Limits: line-level only, no type information. SQL in a multi-line string is missed when the
statement does not start right after the opening quote. A comment marker inside a string
(for example a URL) hides the rest of that line from the checks.
"""
import re
import sys
from pathlib import Path

EXTS = {".ts", ".tsx", ".mts", ".cts"}
REQUIRE_EXTS = {".ts", ".tsx", ".mts"}
LINE_COMMENT = re.compile(r"(^|\s)//.*$")
BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)

CHECKS = [
    (re.compile(r"(:\s*any\b|\bas\s+any\b|<any>)"), "any type: use unknown and narrow it", EXTS),
    (re.compile(r"\bconsole\.log\("), "console.log left in: use the project logger", EXTS),
    (re.compile(r"\beval\(|\bnew\s+Function\("), "dynamic code execution: remove it", EXTS),
    (re.compile(r"\brequire\("), "require in TypeScript: use import", REQUIRE_EXTS),
    (
        re.compile(r"""(["'`])\s*(?:select\b[^"'`]*?\bfrom\b|insert\s+into\b|update\b[^"'`]*?\bset\b|delete\s+from\b)""", re.I),
        "SQL in service code: queries belong to db-query-migration",
        EXTS,
    ),
]

SECRET = re.compile(
    r"""\b\w*(?:password|secret|apikey|api_key|token)\w*\s*(?::\s*[\w<>\[\]| ]+?)?\s*[:=]\s*(["'`])[^"'`\n]{8,}\1""",
    re.I,
)

# Matched against comment-stripped text; each match is a REPORT line.
REPORT_CHECKS = [
    (re.compile(r"[\w)\]]!(?:\.|\))"), "non-null assertion: narrow the value instead"),
    (re.compile(r"\bas\s+unknown\s+as\b"), "as unknown as: fix the type instead of forcing it"),
]
# Matched against the raw text; each match is a REPORT line.
RAW_REPORT_CHECKS = [
    (re.compile(r"\bTODO\b"), "TODO: list it in the report"),
    (re.compile(r"PLACEHOLDER-DATA"), "PLACEHOLDER-DATA: list it in the report"),
]

FRAMEWORK_FLAGS = {"--express": "Express", "--nest": "NestJS"}

EXPRESS_CHECKS = [
    (re.compile(r"\b(?:app|router)\.(?:get|post|put|patch|delete|all)\s*\("), "route handler: handlers belong to api-builder"),
]
NEST_CHECKS = [
    (re.compile(r"@(?:Controller|Get|Post|Put|Patch|Delete|All)\s*\("), "controller or route decorator: belongs to api-builder"),
    (re.compile(r"\bnew\s+\w+(?:Service|Repository)\s*\("), "new on an injectable: let the container provide it"),
]


def strip_comments(text):
    """Blank out comments but keep line breaks, so line numbers stay right."""
    text = BLOCK_COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    return "\n".join(LINE_COMMENT.sub(r"\1", ln) for ln in text.split("\n"))


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def check_framework(text, flags):
    fails = []
    rules = []
    if "--express" in flags:
        rules += EXPRESS_CHECKS
    if "--nest" in flags:
        rules += NEST_CHECKS
    for rx, msg in rules:
        for m in rx.finditer(text):
            fails.append((line_of(text, m.start()), msg))
    return fails


def check_file(path, flags=()):
    fails, reports = [], []
    raw = path.read_text(encoding="utf-8", errors="replace")
    text = strip_comments(raw)
    raw_lines = raw.split("\n")
    ext = path.suffix

    for rx, msg, exts in CHECKS:
        if ext in exts:
            for m in rx.finditer(text):
                fails.append((line_of(text, m.start()), msg))

    # @ts-ignore only appears in comments, so search the raw text, not the comment-stripped text.
    for m in re.finditer(r"@ts-ignore", raw):
        fails.append((line_of(raw, m.start()), "@ts-ignore: use @ts-expect-error with a reason"))

    for m in SECRET.finditer(text):
        ln = line_of(text, m.start())
        if "test-only" in raw_lines[ln - 1]:
            continue
        fails.append((ln, "hard-coded secret: read it from configuration"))

    fails += check_framework(text, flags)

    if "config" not in path.name.lower():
        for m in re.finditer(r"\bprocess\.env\b", text):
            reports.append((line_of(text, m.start()), "process.env outside a config file: read it in one config file"))
    for rx, msg in REPORT_CHECKS:
        for m in rx.finditer(text):
            reports.append((line_of(text, m.start()), msg))
    for rx, msg in RAW_REPORT_CHECKS:
        for m in rx.finditer(raw):
            reports.append((line_of(raw, m.start()), msg))

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
        if p.suffix not in EXTS:
            print(f"SKIP    {p}: not a .ts/.tsx/.mts/.cts file")
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
