#!/usr/bin/env python3
"""Check a spec written by the spec-writer skill against the spec template.

Usage:  python3 -I check_spec.py [--template FILE] SPEC [SPEC ...]

The template defaults to ../assets/spec-template.md next to this script.

Static, line-level checks. They prove the spec is complete in the way the project-planner
needs; they cannot tell whether an answer is right. FAIL exits 1.
Files accepted: .md. Other files print SKIP.

  FAIL    S1  a heading from the template is missing
          S2  a line from the template is missing (a `- Label: <placeholder>` line)
          S3  a template placeholder (such as <draft / ready to plan / revised>) is still there
          S4  a line has a label and no answer, and no lines under it
          S5  TBD, TODO, "to be decided" or "to be determined"
          S6  "Not required" with no ": reason" after it
          S7  an "Undecided" line, but the Open questions table has no row
  REPORT  number of Undecided lines, number of Assumption lines, number of Open questions rows,
          and a Project-type prompts section that was not deleted

Limits: a line is found by its label, so a renamed label counts as missing. Text inside an
HTML comment is ignored. Lines whose label holds a placeholder, such as the "When a reference
conflicts with <...>" line, are not checked.
"""
import re
import sys
from pathlib import Path

DEFAULT_TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "spec-template.md"
COMMENT = re.compile(r"<!--.*?-->", re.S)
HEADING = re.compile(r"^(#{2,6})\s+(.+?)\s*$")
LABEL = re.compile(r"^(\s*)- ([^:<`]{3,80}):(.*)$")
PLACEHOLDER = re.compile(r"<[^<>\n]{6,}>")
NOT_A_LABEL = {"Format", "Example"}
PROMPTS = "Project-type prompts"


def heading_name(line):
    m = HEADING.match(line)
    return m.group(2) if m else None


def strip_comments(text):
    """Blank out HTML comments but keep the line count."""
    return COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def split_template(text):
    """Return (headings, labels, placeholders) from the part of the template a spec keeps."""
    kept = []
    for ln in strip_comments(text).split("\n"):
        m = HEADING.match(ln)
        if m and m.group(2) == PROMPTS:
            break
        kept.append(ln)
    headings, labels, holders = [], [], set()
    for ln in kept:
        m = HEADING.match(ln)
        if m:
            headings.append((len(m.group(1)), m.group(2)))
        lm = LABEL.match(ln)
        if lm and "<" in lm.group(3) and lm.group(2).strip() not in NOT_A_LABEL:
            labels.append(lm.group(2).strip())
        for ph in PLACEHOLDER.findall(ln):
            holders.add(ph)
    return headings, labels, holders


def open_questions_rows(lines):
    """Count data rows of the Open questions table."""
    rows, inside = 0, False
    for ln in lines:
        name = heading_name(ln)
        if name is not None:
            inside = name == "Open questions"
            continue
        if inside and ln.lstrip().startswith("|"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if all(re.fullmatch(r"-+", c) or not c for c in cells):
                continue
            if cells and cells[0].lower() == "question":
                continue
            rows += 1
    return rows


def check_file(path, template):
    headings, labels, holders = template
    raw = path.read_text(encoding="utf-8", errors="replace")
    lines = strip_comments(raw).split("\n")
    fails, reports = [], []

    have = {(len(m.group(1)), m.group(2)) for m in (HEADING.match(ln) for ln in lines) if m}
    for level, name in headings:
        if (level, name) not in have:
            fails.append((1, f'S1 missing heading "{"#" * level} {name}"'))

    spec_labels = set()
    for ln in lines:
        lm = LABEL.match(ln)
        if lm:
            spec_labels.add(lm.group(2).strip())
    for label in labels:
        if label not in spec_labels:
            fails.append((1, f'S2 missing line "- {label}:"'))

    open_at = next((i for i, ln in enumerate(lines) if heading_name(ln) == "Open questions"), len(lines))
    undecided = 0
    for i, ln in enumerate(lines):
        n = i + 1
        for ph in PLACEHOLDER.findall(ln):
            if ph in holders:
                fails.append((n, f"S3 template placeholder still there: {ph}"))
        lm = LABEL.match(ln)
        if lm and not lm.group(3).strip():
            indent = len(lm.group(1))
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            deeper = nxt.strip() and (len(nxt) - len(nxt.lstrip())) > indent and nxt.lstrip().startswith("-")
            if not deeper:
                fails.append((n, f'S4 "{lm.group(2).strip()}" has no answer'))
        if re.search(r"\b(TBD|TODO)\b|to be (decided|determined)", ln, re.I):
            fails.append((n, "S5 TBD or TODO: decide it, or write Undecided and add an Open questions row"))
        if re.search(r"Not required(?!\s*:\s*\S)", ln):
            fails.append((n, 'S6 "Not required" needs a reason: write "Not required: <reason>"'))
        if i < open_at and "Undecided" in ln:
            undecided += 1
    rows = open_questions_rows(lines)
    if undecided and not rows:
        fails.append((1, f"S7 {undecided} Undecided line(s) but the Open questions table has no row"))

    assumptions = sum(1 for ln in lines if re.search(r"\bAssumption:", ln))
    reports.append((1, f"{undecided} Undecided line(s), {assumptions} Assumption line(s), {rows} Open questions row(s)"))
    if any(heading_name(ln) == PROMPTS for ln in lines):
        reports.append((1, "the Project-type prompts section is still there: delete it when the spec is final"))
    return fails, reports


def main(argv):
    args = list(argv)
    template_path = DEFAULT_TEMPLATE
    if "--template" in args:
        i = args.index("--template")
        if i + 1 >= len(args):
            print(__doc__)
            return 2
        template_path = Path(args[i + 1])
        del args[i:i + 2]
    files = [Path(a) for a in args if not a.startswith("--")]
    if not files or any(a.startswith("--") for a in args):
        print(__doc__)
        return 2
    if not template_path.is_file():
        print(f"FAIL    {template_path}: the template does not exist")
        print("RESULT  FAIL")
        return 1
    template = split_template(template_path.read_text(encoding="utf-8", errors="replace"))
    failed = False
    for p in files:
        if not p.is_file():
            print(f"SKIP    {p}: not a file")
            continue
        if p.suffix != ".md":
            print(f"SKIP    {p}: not a .md file")
            continue
        fails, reports = check_file(p, template)
        for ln, msg in fails:
            print(f"FAIL    {p}:{ln}: {msg}")
        for ln, msg in reports:
            print(f"REPORT  {p}:{ln}: {msg}")
        failed = failed or bool(fails)
    print("RESULT  " + ("FAIL" if failed else "PASS"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
