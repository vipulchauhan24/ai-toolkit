#!/usr/bin/env python3
"""Check React files written by the frontend-react skill.

Usage:  python3 -I check_react.py [--next] FILE [FILE ...]

--next adds checks for a Next.js App Router project.

Static, line-level checks. They complement the project's own typecheck and lint
(react-hooks/rules-of-hooks, react-hooks/exhaustive-deps, react/jsx-key), which are
more precise; run those first. FAIL exits 1.

  FAIL    any, @ts-ignore, class components (error boundaries excepted), dangerouslySetInnerHTML
          without a SANITIZED: comment, onClick on div/span, array index or random value as key,
          target="_blank" without rel="noopener", effects and callbacks with no dependency
          array, direct DOM queries, console.log, secrets in client-exposed env variables,
          `list.length && <X />` (renders 0)
  REPORT  fetch inside an effect, useMemo/useCallback/memo (each needs a measured reason),
          in-place .sort()/.reverse()/.splice(), consecutive awaits that may be independent,
          PLACEHOLDER-DATA markers
  --next  FAIL  hooks or handlers in a page/layout without "use client", error.tsx without it,
                ssr:false outside a client file, an async client component, a non-NEXT_PUBLIC
                env variable in a client file
          REPORT  <img> instead of next/image, internal <a href="/..."> instead of next/link,
                hooks in other files with no "use client" (fine if only client files import them)
"""
import re
import sys
from pathlib import Path

EXTS = {".ts", ".tsx", ".js", ".jsx"}
LINE_COMMENT = re.compile(r"(^|\s)//.*$")
BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)

CHECKS = [
    (re.compile(r"(:\s*any\b|\bas\s+any\b|<any>)"), "`any` type: use `unknown` and narrow it", {".ts", ".tsx"}),
    (re.compile(r"@ts-ignore"), "`@ts-ignore`: use `@ts-expect-error` with a reason", {".ts", ".tsx", ".js", ".jsx"}),
    (re.compile(r"<(?:div|span)\b(?:[^>]|=>)*?\bonClick\s*="), "onClick on a div/span: use a <button> or <a>", EXTS),
    (re.compile(r"\bkey=\{[^}]*(?:Math\.random|randomUUID)"), "key generated at render time: use a stable id", EXTS),
    (re.compile(r"\b(?:document\.(?:querySelector|querySelectorAll|getElementById)|getElementsBy\w+)\("), "direct DOM query: use a ref", EXTS),
    (re.compile(r"\bconsole\.log\("), "console.log left in: remove it", EXTS),
    (re.compile(r"\{\s*[\w.?]+\.length\s*&&\s*<"), "`.length && <X />` renders 0: use `.length > 0 ? <X /> : null`", EXTS),
    (re.compile(r"(?:VITE_|NEXT_PUBLIC_|REACT_APP_)\w*(?:SECRET|TOKEN|PASSWORD|PRIVATE)\w*", re.I), "secret in a client-exposed variable", EXTS),
]
HOOKS_NEED_DEPS = ("useEffect", "useLayoutEffect", "useCallback", "useMemo")


def strip_comments(text):
    text = BLOCK_COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    return "\n".join(LINE_COMMENT.sub(r"\1", ln) for ln in text.split("\n"))


def call_args(text, start):
    """Return (args_text, end) for the call whose '(' is at text[start], or None."""
    depth, i, quote = 0, start, None
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == "\\":
                i += 1
            elif ch == quote:
                quote = None
        elif ch in "\"'`":
            quote = ch
        elif ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i
        i += 1
    return None


def top_level_commas(args):
    depth, quote, n, i = 0, None, 0, 0
    while i < len(args):
        ch = args[i]
        if quote:
            if ch == "\\":
                i += 1
            elif ch == quote:
                quote = None
        elif ch in "\"'`":
            quote = ch
        elif ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif ch == "," and depth == 0 and args[i + 1:].strip():
            n += 1
        i += 1
    return n


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


CLIENT_HOOKS = re.compile(r"\b(?:useState|useEffect|useReducer|useRef|useContext|useLayoutEffect|useRouter|usePathname|useSearchParams|useTransition|useActionState)\b|\bon(?:Click|Change|Submit|KeyDown|Input)\s*=")
ROUTE_FILE = re.compile(r"(?:^|/)(?:page|layout|template|loading|default|not-found)\.(?:t|j)sx?$")
ERROR_FILE = re.compile(r"(?:^|/)(?:error|global-error)\.(?:t|j)sx?$")


def has_use_client(raw):
    head = re.sub(r"^(?:\s|//[^\n]*\n|/\*.*?\*/)*", "", raw, flags=re.S)
    return bool(re.match(r"""['"]use client['"]""", head))


def check_next(path, raw, text):
    fails, reports = [], []
    posix = path.as_posix()
    client = has_use_client(raw)
    uses_client_api = bool(CLIENT_HOOKS.search(text))
    if ERROR_FILE.search(posix) and not client:
        fails.append((1, "error file must start with 'use client'"))
    elif ROUTE_FILE.search(posix) and uses_client_api and not client:
        fails.append((1, "page or layout uses hooks or handlers but has no 'use client': move that part into a client component"))
    elif uses_client_api and not client:
        reports.append((1, "uses hooks or handlers with no 'use client': fine only if every importer is a client file"))
    for m in re.finditer(r"ssr\s*:\s*false", text):
        if not client:
            fails.append((line_of(text, m.start()), "ssr: false is only allowed inside a client file"))
    if client and re.search(r"export\s+default\s+async\s+function|export\s+async\s+function\s+[A-Z]", text):
        m = re.search(r"export\s+default\s+async\s+function|export\s+async\s+function\s+[A-Z]", text)
        fails.append((line_of(text, m.start()), "client component cannot be async"))
    if client:
        for m in re.finditer(r"process\.env\.(?!NEXT_PUBLIC_|NODE_ENV)\w+", text):
            fails.append((line_of(text, m.start()), "env variable is not available in the browser and must not hold a secret"))
    for m in re.finditer(r"<img\b", text):
        reports.append((line_of(text, m.start()), "<img>: use next/image"))
    for m in re.finditer(r"<a\b(?:[^>]|=>)*?href=[\"']/(?!/)", text):
        reports.append((line_of(text, m.start()), "internal <a href>: use next/link"))
    return fails, reports


def check_file(path, nxt=False):
    fails, reports = [], []
    raw = path.read_text(encoding="utf-8", errors="replace")
    text = strip_comments(raw)
    raw_lines = raw.split("\n")
    ext = path.suffix

    for rx, msg, exts in CHECKS:
        if ext in exts:
            for m in rx.finditer(text):
                fails.append((line_of(text, m.start()), msg))

    for m in re.finditer(r"<a\b(?:[^>]|=>)*?target=[\"']_blank[\"'](?:[^>]|=>)*>", text):
        if "noopener" not in m.group(0):
            fails.append((line_of(text, m.start()), 'target="_blank" without rel="noopener noreferrer"'))

    for m in re.finditer(r"\bkey=\{\s*(index|idx|i|j|k)\s*\}", text):
        name = m.group(1)
        if re.search(rf",\s*{name}\s*\)\s*=>", text):
            fails.append((line_of(text, m.start()), "array index as key: use a stable id"))

    for m in re.finditer(r"dangerouslySetInnerHTML", text):
        ln = line_of(text, m.start())
        near = "\n".join(raw_lines[max(0, ln - 3):ln])
        if "SANITIZED:" not in near:
            fails.append((ln, "dangerouslySetInnerHTML without a `SANITIZED:` comment saying where"))

    if re.search(r"\bextends\s+(?:React\.)?(?:Pure)?Component\b", text) and not re.search(
        r"componentDidCatch|getDerivedStateFromError", text
    ):
        m = re.search(r"\bextends\s+(?:React\.)?(?:Pure)?Component\b", text)
        fails.append((line_of(text, m.start()), "class component: write a function component"))

    for m in re.finditer(r"\b(useEffect|useLayoutEffect|useCallback|useMemo)\s*\(", text):
        got = call_args(text, m.end() - 1)
        if not got:
            continue
        args, _ = got
        name = m.group(1)
        if name in HOOKS_NEED_DEPS and top_level_commas(args) == 0:
            fails.append((line_of(text, m.start()), f"{name} has no dependency array"))
        if name in ("useEffect", "useLayoutEffect") and re.search(r"\bfetch\s*\(", args):
            reports.append((line_of(text, m.start()), "fetch inside an effect: use the project's data layer if it has one"))
        if name in ("useCallback", "useMemo"):
            reports.append((line_of(text, m.start()), f"{name}: needs a measured reason in a comment"))

    for m in re.finditer(r"\bReact\.memo\(|\bmemo\(", text):
        reports.append((line_of(text, m.start()), "memo: needs a measured reason in a comment"))

    for m in re.finditer(r"(?<!\])\.(?:sort|reverse|splice)\(", text):
        reports.append((line_of(text, m.start()), "in-place mutation: copy first or use toSorted()/toReversed()/toSpliced()"))

    lines = text.split("\n")
    pat = re.compile(r"^\s*(?:const|let)\s+(\w+|\{[^}]*\}|\[[^\]]*\])\s*=\s*await\s")
    for i in range(len(lines) - 1):
        a, b = pat.match(lines[i]), pat.match(lines[i + 1])
        if a and b:
            names = re.findall(r"\w+", a.group(1))
            if not any(re.search(rf"\b{re.escape(n)}\b", lines[i + 1].split("=", 1)[1]) for n in names):
                reports.append((i + 2, "consecutive awaits: use Promise.all if the second does not need the first"))

    if nxt:
        nf, nr = check_next(path, raw, text)
        fails += nf
        reports += nr

    for m in re.finditer(r"PLACEHOLDER-DATA", raw):
        reports.append((line_of(raw, m.start()), "PLACEHOLDER-DATA: list it in the report"))

    return sorted(set(fails)), sorted(set(reports))


def main(argv):
    nxt = "--next" in argv
    files = [Path(a) for a in argv if a != "--next"]
    if not files:
        print(__doc__)
        return 2
    failed = False
    for p in files:
        if not p.is_file():
            print(f"SKIP    {p}: not a file")
            continue
        if p.suffix not in EXTS:
            print(f"SKIP    {p}: not a .ts/.tsx/.js/.jsx file")
            continue
        fails, reports = check_file(p, nxt)
        for ln, msg in fails:
            print(f"FAIL    {p}:{ln}: {msg}")
        for ln, msg in reports:
            print(f"REPORT  {p}:{ln}: {msg}")
        failed = failed or bool(fails)
    print("RESULT  " + ("FAIL" if failed else "PASS"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
