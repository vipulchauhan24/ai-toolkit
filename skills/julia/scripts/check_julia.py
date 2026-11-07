#!/usr/bin/env python3
"""Check Julia files written by the julia skill.

Usage:  python3 -I check_julia.py FILE [FILE ...]

Static, line-level checks on comment-stripped text (comments are `#` to end of
line and `#= ... =#`). They complement the project's own tests; run those first.
There is no framework flag: the rules apply to every Julia file. No type
inference is done, so type stability is not checked (use `@code_warntype`).
Only .jl files are checked; other files print SKIP. FAIL exits 1; no file exits 2.

  FAIL    J1  eval( or @eval                                            dynamic code execution
  FAIL    J2  Pkg.add(, Pkg.develop( or `using Pkg` in a file under src/ package management in source
  FAIL    J3  @show                                                     left in
  FAIL    J4  a catch block with an empty body (multi-line or `catch; end`)
  FAIL    J5  ::Any in an annotation
  FAIL    J6  @get, @post, @put, @patch, @delete or @route at the start of a line (Oxygen handler)
  FAIL    J7  LibPQ., SQLite., MySQL., Mongoc. or DBInterface.execute( (database access)
  FAIL    J8  password/secret/api_key/token name assigned a string literal of 8+ characters
  FAIL    J9  a string literal beginning "/home/, "/Users/ or "C:\\
  REPORT  non-const global (top-level assignment that is not const/using/import/function/struct/module/export/include)
  REPORT  rand( in a file with none of Random.seed!, Xoshiro(, MersenneTwister(
  REPORT  `for ... in eachrow(` loop
  REPORT  include( inside a src/ module file (only the top-level file directly in src/ may include)
  REPORT  TODO
  REPORT  PLACEHOLDER-DATA
"""
import re
import sys
from pathlib import Path

LANG_EXT = {".jl"}
BLOCK_COMMENT = re.compile(r"#=.*?=#", re.S)
LINE_COMMENT = re.compile(r"(^|\s)#.*$")

IN_SRC = "src"  # J2 applies to files with a `src` folder in their path

# (id, compiled regex, message, only_in_src)
CHECKS = [
    ("J1", re.compile(r"\beval\(|@eval\b"), "dynamic code execution: remove it", False),
    ("J2", re.compile(r"\bPkg\.(?:add|develop)\(|\busing\s+Pkg\b"),
     "package management in source: use the project environment", True),
    ("J3", re.compile(r"@show\b"), "@show left in: use @info or remove it", False),
    ("J4", re.compile(r"\bcatch\b(?:[ \t]+[A-Za-z_]\w*)?[ \t]*(?:;|\n)\s*end\b"),
     "empty catch: handle the error or rethrow", False),
    ("J5", re.compile(r"::Any\b"), "::Any annotation: use a concrete type", False),
    ("J6", re.compile(r"^[ \t]*@(?:get|post|put|patch|delete|route)\b", re.M),
     "Oxygen route handler: handlers belong to api-builder", False),
    ("J7", re.compile(r"\b(?:LibPQ|SQLite|MySQL|Mongoc)\.|\bDBInterface\.execute\("),
     "database access: belongs to the database skills", False),
    ("J8", re.compile(r"\b\w*(?:password|secret|api_key|token)\w*[ \t]*=(?!=)[ \t]*\"[^\"\n]{8,}\"", re.I),
     "hard-coded secret: read it from the environment", False),
    ("J9", re.compile(r"\"(?:/home/|/Users/|C:\\{1,2})"),
     "absolute user path: use a relative path", False),
]

# Matched against comment-stripped text.
GLOBAL_ASSIGN = re.compile(r"^[A-Za-z_]\w*(?:::[^=\n]+?)?[ \t]*=(?!=)", re.M)
RAND = re.compile(r"\brand\(")
SEEDED = re.compile(r"Random\.seed!|\bXoshiro\(|\bMersenneTwister\(")
EACHROW = re.compile(r"\bfor\b[^\n]*\bin\s+eachrow\(")
INCLUDE = re.compile(r"\binclude\(")
# Matched against the raw text.
RAW_REPORTS = [
    (re.compile(r"\bTODO\b"), "TODO: resolve it or list it in the report"),
    (re.compile(r"PLACEHOLDER-DATA"), "PLACEHOLDER-DATA: list it in the report"),
]


def strip_comments(text):
    """Blank out comments but keep line breaks, so line numbers stay right."""
    text = BLOCK_COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    return "\n".join(LINE_COMMENT.sub(r"\1", ln) for ln in text.split("\n"))


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def check_file(path):
    fails, reports = [], []
    raw = path.read_text(encoding="utf-8", errors="replace")
    text = strip_comments(raw)
    parts = path.parts
    in_src = IN_SRC in parts[:-1]

    for _id, rx, msg, only_src in CHECKS:
        if only_src and not in_src:
            continue
        for m in rx.finditer(text):
            fails.append((line_of(text, m.start()), msg))

    for m in GLOBAL_ASSIGN.finditer(text):
        reports.append((line_of(text, m.start()), "non-const global: use const"))
    if not SEEDED.search(text):
        for m in RAND.finditer(text):
            reports.append((line_of(text, m.start()), "rand( with no seed: seed the generator"))
    for m in EACHROW.finditer(text):
        reports.append((line_of(text, m.start()), "loop over eachrow: use select, transform or combine"))
    if in_src and path.parent.name != IN_SRC:
        for m in INCLUDE.finditer(text):
            reports.append((line_of(text, m.start()), "include( inside a src/ module: include only in the top-level module"))
    for rx, msg in RAW_REPORTS:
        for m in rx.finditer(raw):
            reports.append((line_of(raw, m.start()), msg))

    return sorted(set(fails)), sorted(set(reports))


def main(argv):
    files = [Path(a) for a in argv if not a.startswith("--")]
    if not files or len(files) != len(argv):
        print(__doc__)
        return 2
    failed = False
    for p in sorted(files, key=str):
        if not p.is_file():
            print(f"SKIP    {p}: not a file")
            continue
        if p.suffix not in LANG_EXT:
            print(f"SKIP    {p}: not a .jl file")
            continue
        fails, reports = check_file(p)
        for ln, msg in fails:
            print(f"FAIL    {p}:{ln}: {msg}")
        for ln, msg in reports:
            print(f"REPORT  {p}:{ln}: {msg}")
        failed = failed or bool(fails)
    print("RESULT  " + ("FAIL" if failed else "PASS"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
