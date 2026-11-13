#!/usr/bin/env python3
"""Test harness for the ai-toolkit plugin. Standard library only, Python 3.9 or later.

Usage (from the repository root):

    python3 -I tests/run.py static
    python3 -I tests/run.py scripts
    python3 tests/run.py cases --list
    python3 tests/run.py cases [--tier fast|slow|network] [--case ID ...] [--jobs N]
                               [--log PATH | --no-log] [--no-retry]

Layers
  static   Structure of manifests, skills, agents, rules files, cross-references,
           skill folder shape, SKILL.md length, front matter, contents lists and
           shared files. Offline, no model, a few seconds.
  scripts  Check scripts run against clean and seeded fixtures. Offline, no model.
  cases    Skills and agents run through `claude -p` with the plugin loaded from
           this checkout, then asserted. Needs the `claude` CLI and uses tokens.

Output lines start with PASS, FAIL, WARN, XFAIL, XPASS, RETRY or RESULT. A run
passes when it prints `RESULT  PASS`. FAIL and XPASS lines fail the run; WARN and
XFAIL lines are listed in the release notes and do not.

Tiers: fast (under about a minute each), slow (several minutes), network (needs
internet). `--tier fast` runs fast; `--tier slow` runs fast and slow
(the default); `--tier network` runs network only.

Case files are tests/cases/*.json (see tests/README.md for the format).
"""
from __future__ import annotations

import argparse
import ast
import concurrent.futures
import datetime
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests"
FIXTURES = TESTS / "fixtures"
CASES = TESTS / "cases"
RUNS = TESTS / "runs"
PY = [sys.executable, "-I", "-B"]

SKILL_KEYS = ("name", "description", "license", "compatibility", "model")
SKILL_ENTRIES = {"SKILL.md", "references", "scripts", "assets"}
# Rules files whose contents list is a hard rule (release checklist step 3).
CONTENTS_RULES = re.compile(
    r"(react|nextjs|node|express|nestjs|python|django|fastapi|julia|api|postgres|mysql|mongodb)-rules\.md$"
    r"|architecture-patterns\.md$|react-performance-guidelines\.md$"
)
# Rules files that a model case must cover.
COVER_RULES = re.compile(r"-rules\.md$|^architecture-patterns\.md$|^react-performance-guidelines\.md$")
DEFAULT_PATTERNS = {
    "React": "mvvm",
    "Next.js": "layered",
    "Express": "layered",
    "NestJS": "layered",
    "FastAPI": "layered",
    "Django": "mvc",
    "Oxygen": "layered",
}
# Every script under skills/*/scripts needs a test. Later skill phases add their own entry.
SCRIPT_COVERAGE = {
    "skills/frontend-react/scripts/check_react.py": "tests/fixtures/frontend-react",
    "skills/backend-node/scripts/check_node.py": "tests/fixtures/backend-node",
    "skills/backend-python/scripts/check_python.py": "tests/fixtures/backend-python",
    "skills/julia/scripts/check_julia.py": "tests/fixtures/julia",
    "skills/orchestrator/scripts/engine.py": "tests/fixtures/orchestrator",
    "skills/spec-writer/scripts/check_spec.py": "tests/fixtures/spec-writer",
    "skills/copy-writer/scripts/check_copy.py": "tests/fixtures/ui-craft",
    "skills/ui-craft/scripts/check_copy.py": "tests/fixtures/ui-craft",
    "skills/ui-craft/scripts/contrast.py": "tests/fixtures/ui-craft",
    "skills/ui-craft/scripts/icons.py": "tests/fixtures/ui-craft",
    "skills/ui-craft/scripts/audit.py": "tests/fixtures/ui-craft",
    "skills/design-md/scripts/deal.py": "tests/fixtures/ui-craft",
    "skills/design-md/scripts/contrast.py": "tests/fixtures/ui-craft",
    "skills/design-md/scripts/audit.py": "tests/fixtures/ui-craft",
    "skills/design-md/scripts/sameness.py": "tests/fixtures/ui-craft",
    "skills/design-md/scripts/preview.py": "tests/fixtures/ui-craft",
    "skills/design-md/scripts/colors.py": "tests/fixtures/ui-craft",
    "skills/visual-qa/scripts/capture.py": "tests/fixtures/visual-qa",
    "skills/visual-qa/scripts/report.py": "tests/fixtures/visual-qa",
    "skills/visual-qa/scripts/page_checks.js": "tests/fixtures/visual-qa",
    "skills/visual-qa/scripts/steps.js": "tests/fixtures/visual-qa",
}
REQUIRED_FIXTURES = [
    "doc-trimmer",
    "doc-reviewer",
    "project-planner-pattern",
    "project-planner-pattern/sample-project",
    "project-planner-pattern/conflicting-spec.md",
    "project-planner-greenfield",
    "frontend-react-projects",
    "skill-runner",
    "orchestrator",
    "orchestrator-projects",
    "spec-writer",
    "spec-writer-projects",
    "copy-writer-projects",
    "ui-craft",
    "ui-craft-projects",
    "design-md-projects",
    "visual-qa",
    "visual-qa/capture",
    "visual-qa/capture-injection",
    "empty",
]
CASE_KEYS = {
    "id", "tier", "fixture", "covers", "source", "prompt", "tools", "skills", "agents", "reads",
    "must", "must_not", "files", "no_files", "unchanged", "post", "timeout",
}
CASE_REQUIRED = ("id", "tier", "fixture", "covers", "source", "prompt")
TIERS = ("fast", "slow", "network")
DEFAULT_TOOLS = "Read,Glob,Grep,Skill"
README_SECTIONS = [
    "## Releasing",
    "## Versioning",
    "## Getting Help",
    "## Testing the Check Scripts",
    "## Testing Skills and Rules",
]


class Report:
    def __init__(self):
        self.failed = 0
        self.warned = 0

    def ok(self, name, detail=""):
        print("PASS    " + name + (": " + detail if detail else ""))

    def fail(self, name, detail=""):
        self.failed += 1
        print("FAIL    " + name + (": " + detail if detail else ""))

    def warn(self, name, detail=""):
        self.warned += 1
        print("WARN    " + name + (": " + detail if detail else ""))

    def note(self, tag, name, detail=""):
        print(tag.ljust(8) + name + (": " + detail if detail else ""))

    def check(self, name, cond, detail=""):
        if cond:
            self.ok(name)
        else:
            self.fail(name, detail)
        return bool(cond)

    def finish(self):
        print("RESULT  " + ("FAIL" if self.failed else "PASS"))
        return 1 if self.failed else 0


# ---------------------------------------------------------------- helpers


def rel(path):
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def read(path):
    return Path(path).read_text(encoding="utf-8", errors="replace")


def front_matter(text):
    """Parse the leading --- block: `key: value`, plus `>` and `|` block scalars."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    out, key, block = {}, None, []
    for ln in lines[1:]:
        if ln.strip() == "---":
            break
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", ln)
        if m and not ln.startswith(" "):
            if key is not None and block:
                out[key] = " ".join(b.strip() for b in block if b.strip())
            key, val = m.group(1), m.group(2).strip()
            block = []
            if val in (">", "|", ">-", "|-"):
                out[key] = ""
            else:
                out[key] = val.strip("\"'")
                key = None
        elif key is not None:
            block.append(ln)
    else:
        return None
    if key is not None and block:
        out[key] = " ".join(b.strip() for b in block if b.strip())
    return out


def run_py(script, args, cwd=None, timeout=120):
    cmd = PY + [str(script)] + [str(a) for a in args]
    p = subprocess.run(cmd, cwd=str(cwd or ROOT), capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout + p.stderr


def contents_problem(text):
    """Same rule as release checklist step 3. Returns None, 'NO CONTENTS' or 'MISMATCH'."""
    t = text.split("\n")
    if len(t) <= 100:
        return None
    if "## Contents" not in t:
        return "NO CONTENTS"
    heads = [re.sub(r"^\d+\.\s*", "", ln[3:]).strip() for ln in t if ln.startswith("## ") and ln != "## Contents"]
    items = []
    for ln in t[t.index("## Contents") + 1:]:
        if not ln.strip():
            if items:
                break
            continue
        m = re.match(r"\d+\.\s*(.*)", ln)
        if not m:
            break
        items.append(m.group(1).strip())
    return None if items == heads else "MISMATCH"


def skill_dirs():
    return sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())


def rules_files(pattern):
    out = []
    for f in sorted(glob.glob(str(ROOT / "skills" / "*" / "references" / "*.md"))):
        p = Path(f)
        if pattern.search(p.name if pattern is COVER_RULES else rel(p)):
            out.append(p)
    return out


def load_cases():
    """Return (cases, errors). Each case gets `_file` set."""
    cases, errors = [], []
    for f in sorted(CASES.glob("*.json")):
        try:
            data = json.loads(read(f))
        except ValueError as e:
            errors.append("%s: invalid JSON: %s" % (f.name, e))
            continue
        if not isinstance(data, list):
            errors.append("%s: must hold a list of cases" % f.name)
            continue
        for c in data:
            if isinstance(c, dict):
                c["_file"] = f.name
                cases.append(c)
            else:
                errors.append("%s: every case must be an object" % f.name)
    return cases, errors


def source_exists(source):
    """`doc-trimmer.md: Functional / File input` -> heading and bold label exist in tests/doc-trimmer.md."""
    m = re.match(r"^([\w.-]+\.md):\s*(.+?)(?:\s*/\s*(.+))?$", source)
    if not m:
        return "not of the form '<file>.md: <Heading> [/ <Label>]'"
    fname, heading, label = m.group(1), m.group(2).strip(), m.group(3)
    f = TESTS / fname
    if not f.is_file():
        return "tests/%s does not exist" % fname
    text = read(f)
    if not re.search(r"^#{1,6}\s+%s\s*$" % re.escape(heading), text, re.M):
        return "heading '%s' not found in tests/%s" % (heading, fname)
    if label and not re.search(r"^\*\*%s\*\*\s*$" % re.escape(label.strip()), text, re.M):
        return "label '%s' not found in tests/%s" % (label.strip(), fname)
    return None


def regexes_ok(value):
    if not isinstance(value, list):
        return False
    for rx in value:
        try:
            re.compile(rx)
        except (re.error, TypeError):
            return False
    return True


# ---------------------------------------------------------------- static


def cmd_static(_args):
    r = Report()
    skills = skill_dirs()

    # Manifests
    try:
        plugin = json.loads(read(ROOT / ".claude-plugin" / "plugin.json"))
        market = json.loads(read(ROOT / ".claude-plugin" / "marketplace.json"))
    except (ValueError, OSError) as e:
        r.fail("manifests parse", str(e))
        return r.finish()
    mp = market["plugins"][0]
    r.check("manifests: plugin.json and marketplace.json versions match", plugin.get("version") == mp.get("version"),
            "%s vs %s" % (plugin.get("version"), mp.get("version")))
    r.check("manifests: plugin names match", plugin.get("name") == mp.get("name"), "%s vs %s" % (plugin.get("name"), mp.get("name")))
    r.check("manifests: marketplace source is the repository root", mp.get("source") == "./", str(mp.get("source")))
    for p in plugin.get("skills", []):
        r.check("manifests: plugin.json path exists: " + p, (ROOT / p).exists())

    # Skills
    for sd in skills:
        name = sd.name
        sm = sd / "SKILL.md"
        if not r.check("skill %s: SKILL.md exists" % name, sm.is_file()):
            continue
        text = read(sm)
        fm = front_matter(text)
        if not r.check("skill %s: front matter parses" % name, fm is not None):
            continue
        missing = [k for k in SKILL_KEYS if not fm.get(k)]
        r.check("skill %s: front matter has %s" % (name, ", ".join(SKILL_KEYS)), not missing, "missing " + ", ".join(missing))
        r.check("skill %s: name matches the folder" % name, fm.get("name") == name, "name is %r" % fm.get("name"))
        desc = fm.get("description", "")
        r.check("skill %s: description under 1024 characters, no < or >" % name,
                0 < len(desc) < 1024 and "<" not in desc and ">" not in desc,
                "%d characters" % len(desc))
        lines, words = len(text.split("\n")) - 1, len(text.split())
        r.check("skill %s: SKILL.md under 500 lines and 5,000 words" % name, lines < 500 and words < 5000,
                "%d lines, %d words" % (lines, words))
        extra = sorted(e.name for e in sd.iterdir() if e.name not in SKILL_ENTRIES)
        r.check("skill %s: folder holds only SKILL.md, references/, scripts/, assets/" % name, not extra, "found " + ", ".join(extra))
        r.check("skill %s: no README in the skill folder" % name, not [p for p in sd.rglob("*") if p.name.lower().startswith("readme")])
        refs = set()
        for m in re.finditer(r"(?<![\w/-])((?:references|scripts|assets)/[A-Za-z0-9_./-]+)", text):
            refs.add(m.group(1).rstrip(".,;:)"))
        for ref in sorted(refs):
            r.check("skill %s: referenced path exists: %s" % (name, ref), (sd / ref).exists())

    # Agents
    for ag in sorted((ROOT / "agents").glob("*.md")):
        fm = front_matter(read(ag))
        if not r.check("agent %s: front matter parses" % ag.name, fm is not None):
            continue
        missing = [k for k in ("name", "description", "tools") if not fm.get(k)]
        r.check("agent %s: front matter has name, description, tools" % ag.name, not missing, "missing " + ", ".join(missing))
        r.check("agent %s: name matches the file" % ag.name, fm.get("name") == ag.stem, "name is %r" % fm.get("name"))

    # Script syntax at Python 3.9, and shell syntax
    py_files = sorted(glob.glob(str(ROOT / "skills" / "*" / "scripts" / "*.py"))) + sorted(glob.glob(str(ROOT / "scripts" / "*.py"))) + [str(TESTS / "run.py")]
    for f in py_files:
        try:
            ast.parse(read(f), filename=f, feature_version=(3, 9))
            r.ok("python 3.9 syntax: " + rel(f))
        except SyntaxError as e:
            r.fail("python 3.9 syntax: " + rel(f), str(e))
    for f in sorted(glob.glob(str(ROOT / "skills" / "*" / "scripts" / "*.sh"))):
        p = subprocess.run(["bash", "-n", f], capture_output=True, text=True)
        r.check("shell syntax: " + rel(f), p.returncode == 0, p.stderr.strip())

    # Every script has a test
    for f in sorted(glob.glob(str(ROOT / "skills" / "*" / "scripts" / "*"))):
        key = rel(f)
        if key.endswith("__pycache__"):
            continue
        cov = SCRIPT_COVERAGE.get(key)
        r.check("script has a test: " + key, bool(cov) and (ROOT / cov).exists(),
                "add it to SCRIPT_COVERAGE in tests/run.py with a fixture folder")

    # Contents lists
    for f in sorted(glob.glob(str(ROOT / "skills" / "*" / "references" / "*.md"))):
        key = rel(f)
        problem = contents_problem(read(f))
        if CONTENTS_RULES.search(key):
            r.check("contents list: " + key, problem is None, problem or "")
        elif problem:
            r.warn("contents list: " + key, problem + " (not a rules file named in release step 3; owner decides)")

    # Rules read by a skill
    for f in rules_files(COVER_RULES):
        skill_md = read(f.parent.parent / "SKILL.md")
        r.check("rules file is read by its skill: " + rel(f), f.name in skill_md, "%s is not named in SKILL.md" % f.name)

    # Defaults table
    table = {}
    ap = ROOT / "skills" / "project-planner" / "references" / "architecture-patterns.md"
    if ap.is_file():
        for m in re.finditer(r"^\|\s*([^|]+?)\s*\|\s*(mvc|mvvm|layered)\s*\|\s*$", read(ap), re.M):
            table[m.group(1)] = m.group(2)
    wrong = {k: (table.get(k), v) for k, v in DEFAULT_PATTERNS.items() if table.get(k) != v}
    r.check("defaults table in architecture-patterns.md", not wrong, "differs: %s" % wrong)

    # Shared files
    rc, out = run_py(ROOT / "scripts" / "check_shared_files.py", [])
    bad = [ln for ln in out.splitlines() if ln.startswith(("MISSING", "DIFFERS"))]
    r.check("shared files match scripts/shared_files.json", rc == 0 and not bad, "; ".join(bad) or out.strip()[-200:])

    ui_craft_reference_checks(r)

    # Readme and ignore file
    readme = read(ROOT / "README.md")
    heads = [ln for ln in readme.split("\n") if ln.startswith("## ")]
    try:
        i, j = heads.index("## Repository Layout"), heads.index("## License")
        between = heads[i + 1:j]
    except ValueError:
        between = []
    r.check("README release sections, in order, between Repository Layout and License", between == README_SECTIONS,
            "found %s" % between)
    r.check("README layout table has a tests/ row", bool(re.search(r"^\|\s*`tests/`\s*\|.*fixtures.*run logs", readme, re.M | re.I)))
    r.check("README names Python 3.9 or later on Linux and macOS",
            bool(re.search(r"Python 3\.9 or later", readme)) and "Linux and macOS" in readme)
    gi = read(ROOT / ".gitignore").split("\n")
    r.check(".gitignore ignores tests/runs/.cases/", "tests/runs/.cases/" in gi)
    r.check(".gitignore does not ignore run logs (tests/runs/)", "tests/runs/" not in gi and "tests/runs" not in gi)

    # Case fixtures
    for fx in REQUIRED_FIXTURES:
        r.check("fixture exists: tests/fixtures/" + fx, (FIXTURES / fx).exists())

    # Cases: schema, sources, coverage
    cases, errors = load_cases()
    for e in errors:
        r.fail("case files", e)
    ids = set()
    for c in cases:
        cid = c.get("id", "?")
        label = "case %s" % cid
        unknown = sorted(set(c) - CASE_KEYS - {"_file"})
        missing = [k for k in CASE_REQUIRED if k not in c]
        r.check(label + ": schema", not unknown and not missing,
                "unknown keys %s, missing keys %s" % (unknown, missing))
        if missing:
            continue
        r.check(label + ": id is unique kebab-case", cid not in ids and re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", cid) is not None)
        ids.add(cid)
        r.check(label + ": tier is fast, slow or network", c["tier"] in TIERS, str(c["tier"]))
        r.check(label + ": fixture folder exists", (FIXTURES / c["fixture"]).is_dir(), c["fixture"])
        r.check(label + ": regex fields compile", all(regexes_ok(c.get(k, [])) for k in ("skills", "agents", "reads", "must", "must_not")))
        has_assert = any(c.get(k) for k in ("skills", "agents", "reads", "must", "must_not", "files", "no_files", "unchanged", "post"))
        r.check(label + ": asserts something", has_assert)
        bad_cover = [p for p in c["covers"] if not (ROOT / p).exists()]
        r.check(label + ": covers paths exist", bool(c["covers"]) and not bad_cover, "missing %s" % bad_cover)
        problem = source_exists(c["source"])
        r.check(label + ": source names an existing heading", problem is None, problem or "")
        for pattern in c.get("unchanged", []):
            r.check(label + ": unchanged file exists in the fixture: " + pattern, (FIXTURES / c["fixture"] / pattern).exists())

    covered = set()
    for c in cases:
        covered.update(c.get("covers", []))
    for sd in skills:
        r.check("covered by at least one model case: skills/" + sd.name, ("skills/" + sd.name) in covered)
    for ag in sorted((ROOT / "agents").glob("*.md")):
        r.check("covered by at least one model case: agents/" + ag.name, ("agents/" + ag.name) in covered)
    for f in rules_files(COVER_RULES):
        if f.stat().st_size > 0:
            r.check("covered by at least one model case: " + rel(f), rel(f) in covered)

    return r.finish()


# ---------------------------------------------------------------- scripts


def check_scripts_for(skill):
    d = ROOT / "skills" / skill / "scripts"
    return sorted(list(d.glob("check_*.py")) + list(d.glob("audit_*.py")))


def cmd_scripts(_args):
    r = Report()

    # Fixture sets: tests/fixtures/<skill>/<flag-set>/{clean,seeded}
    for clean in sorted(glob.glob(str(FIXTURES / "*" / "*" / "clean"))):
        clean = Path(clean)
        set_dir = clean.parent
        skill, flagset = set_dir.parent.name, set_dir.name
        tag = "%s/%s" % (skill, flagset)
        scripts = check_scripts_for(skill)
        if not r.check("%s: exactly one check script" % skill, len(scripts) == 1, "found %d" % len(scripts)):
            continue
        script = scripts[0]
        flag = [] if flagset == "base" else ["--" + flagset]
        exp_path = set_dir / "expected.json"
        if not r.check("%s: expected.json exists" % tag, exp_path.is_file()):
            continue
        exp = json.loads(read(exp_path))
        xfail = exp.get("xfail", {})

        files = sorted(p for p in clean.rglob("*") if p.is_file())
        r.check("%s clean: holds %s file(s)" % (tag, exp.get("clean_files")), len(files) == exp.get("clean_files"), "found %d" % len(files))
        if files:
            rc, out = run_py(script, flag + [rel(p) for p in files])
            result = [ln for ln in out.splitlines() if ln.startswith("RESULT")]
            good = rc == 0 and (not result or result[-1].split() == ["RESULT", "PASS"])
            r.check("%s clean: exits 0 and passes" % tag, good, "exit %d; %s" % (rc, "; ".join(ln for ln in out.splitlines() if ln.startswith("FAIL"))[:300]))

        seeded_dir = set_dir / "seeded"
        on_disk = sorted(p.relative_to(seeded_dir).as_posix() for p in seeded_dir.rglob("*") if p.is_file())
        expected_names = sorted(exp.get("seeded", {}))
        r.check("%s seeded: files match expected.json (%d)" % (tag, len(expected_names)), on_disk == expected_names,
                "on disk %s, expected %s" % (on_disk, expected_names))
        for name in expected_names:
            pattern = exp["seeded"][name]
            f = seeded_dir / name
            if not f.is_file():
                continue
            rc, out = run_py(script, flag + [rel(f)])
            fails = [ln for ln in out.splitlines() if ln.startswith("FAIL")]
            hits = [ln for ln in fails if re.search(pattern, ln)]
            extra = [ln for ln in fails if ln not in hits]
            label = "%s seeded %s" % (tag, name)
            if hits and rc == 1:
                if name in xfail:
                    r.fail(label, "XPASS: rule now fires (%s); remove it from xfail" % xfail[name])
                elif extra:
                    r.fail(label, "also fails for another reason: " + extra[0].strip())
                else:
                    msg = re.sub(r"\s+", " ", hits[0]).strip()
                    r.ok(label, msg)
            elif name in xfail:
                r.note("XFAIL", label, xfail[name])
            else:
                r.fail(label, "exit %d, no FAIL line matching %r. Output: %s" % (rc, pattern, re.sub(r"\s+", " ", out).strip()[:200]))

    # Usage errors: no files given
    react = ROOT / "skills" / "frontend-react" / "scripts" / "check_react.py"
    for label, script, args in (
        ("check_react.py with no file", react, []),
        ("check_react.py with only --next", react, ["--next"]),
    ):
        rc, out = run_py(script, args)
        r.check("usage error: %s exits 2" % label, rc == 2, "exit %d" % rc)

    engine_tests(r)
    visual_qa_tests(r)
    copy_check_tests(r)
    ui_craft_script_tests(r)
    showcase_tests(r)

    return r.finish()


# Route files that the orchestrator engine must refuse, and the FAIL line each must print.
ENGINE_BAD_ROUTES = {
    "bad-cycle": r"dependency cycle among",
    "bad-missing-dependency": r"p4: depends on p9, which is not a phase",
    "bad-file-clash": r"p4 and p6 can run together but both change skills/node/SKILL\.md",
    "bad-duplicate-id": r"duplicate phase id p4",
    "bad-no-skills": r"p4: skills must be a non-empty list",
    "bad-parked-no-reason": r"p8: a parked phase needs a park_reason",
    "bad-self-dependency": r"p3: depends on itself",
    "bad-isolation": r"p1: isolation must be",
    "bad-worker-cap": r"max_parallel must be",
    "bad-pattern-file": r"p4: files must be paths or directories ending in /, not patterns",
    "bad-prefix-clash": r"p4 and p5 can run together but both change skills/py/SKILL\.md",
    "bad-main-session-not-parked": r"p4: main_session_skill only belongs on a parked phase",
    "bad-both-session-keys": r"p1: set main_session_skills or the old main_session_skill, not both",
    "bad-look-no-dependency": r"p2: its look is from DESIGN\.md, so it must depend on the Design direction phase",
    "bad-look-after-copy-only": r"p2: its look is from DESIGN\.md, so it must depend on the Design direction phase",
}


def ui_craft_reference_checks(r):
    """ui-craft stays consistent: one token list, and references that point at real files."""
    base = ROOT / "skills" / "ui-craft" / "references"
    system = base / "system" / "system.md"
    if not system.is_file():
        return
    defined = set(re.findall(r"`(--[a-z0-9-]+)`", read(system)))
    files = sorted(f for d in ("system", "components", "sections") for f in (base / d).glob("*.md"))
    used, broken = {}, []
    for f in files:
        text = read(f)
        for token in re.findall(r"(?<![\w-])--[a-z][a-z0-9-]*", text):
            if not token.endswith("-") and token not in defined:
                used.setdefault(token, set()).add(f.name)
        for ref in re.findall(r"`((?:\.\./)?[\w/-]+\.md)`", text):
            if ref not in ("DESIGN.md", "COPY.md") and not (f.parent / ref).exists():
                broken.append("%s -> %s" % (f.name, ref))
    r.check("ui-craft: every token used is defined in system.md", not used, str(used)[:300])
    r.check("ui-craft: every file a reference names exists", not broken, "; ".join(broken)[:300])
    # The kit agrees with the token list, and every sample is complete.
    kit = ROOT / "skills" / "ui-craft" / "assets" / "kit"
    token_file = read(kit / "base" / "tokens.css")
    in_tokens = set(re.findall(r"(--[a-z][a-z0-9-]*):", token_file))
    r.check("ui-craft: every token in system.md has a value in tokens.css", defined <= in_tokens, str(sorted(defined - in_tokens))[:300])
    unknown = {}
    for f in sorted(kit.rglob("*.css")):
        if "examples" in f.parts:
            continue
        for token in re.findall(r"var\((--[a-z][a-z0-9-]*)", read(f)):
            if token not in defined and not token.startswith("--_"):
                unknown.setdefault(token, set()).add(f.name)
    r.check("ui-craft: kit CSS uses only listed tokens", not unknown, str(unknown)[:300])
    missing_links, no_markers = [], []
    for f in sorted(kit.rglob("*.html")):
        text = read(f)
        if "sample:start" not in text or "sample:end" not in text:
            no_markers.append(rel(f))
        for ref in re.findall(r'(?:href|src)="([^"#:]+\.(?:css|js|svg))"', text):
            if not (f.parent / ref).exists():
                missing_links.append("%s -> %s" % (f.name, ref))
    r.check("ui-craft: every file a kit sample loads exists", not missing_links, "; ".join(missing_links)[:300])
    r.check("ui-craft: every kit sample has sample markers", not no_markers, ", ".join(no_markers)[:300])
    kinds = json.loads(read(ROOT / "skills" / "design-md" / "assets" / "data" / "site-kinds.json"))
    absent = []
    for kind in kinds.values():
        absent += ["hero/" + h["id"] for h in kind["heroes"] if not (kit / "sections" / "hero" / (h["id"] + ".html")).is_file()]
        for s in kind["sections"]:
            absent += [s["id"] + "/" + v["id"] for v in s["variants"] if not (kit / "sections" / s["id"] / (v["id"] + ".html")).is_file()]
    r.check("ui-craft: every variant the picker can choose exists in the kit", not absent, ", ".join(absent)[:300])
    r.check("ui-craft: no page shell is offered as a model", all("shell" not in kind for kind in kinds.values()) and "as the model" not in read(ROOT / "skills" / "ui-craft" / "SKILL.md"))
    motion = read(kit / "motion" / "motion.js")
    still_block = re.search(r"if \(!still\) \{(.*?)\n\}", motion[motion.rindex("if (!still)"):], re.S)
    r.check("ui-craft: parallax only runs without reduced motion", still_block is not None and "parallax();" in still_block.group(1) and motion.count("parallax();") == 1)
    r.check("ui-craft: parallax is static below 768px", 'matchMedia("(min-width: 768px)")' in motion)
    r.check("ui-craft: parallax sets its transform only from the script", "transform" not in re.sub(r"prefers-reduced-motion.*", "", "".join(ln for ln in read(kit / "motion" / "motion.css").splitlines() if "data-parallax" in ln)))
    rc, out = run_py(ROOT / "skills" / "ui-craft" / "scripts" / "audit.py", [kit])
    r.check("ui-craft: the kit passes its own audit", rc == 0, out[-300:])
    rc, out = run_py(ROOT / "skills" / "ui-craft" / "scripts" / "contrast.py", [ROOT / "skills" / "design-md" / "assets" / "data" / "palettes.json"])
    r.check("ui-craft: every palette passes the contrast check", rc == 0, out[-300:])

    links = [rel(f) for f in sorted(base.rglob("*.md")) if f.name not in ("NOTICE.md", "review.md") and "http" in read(f)]
    r.check("ui-craft: working files hold rules only, with no links", not links, ", ".join(links))


def copy_check_tests(r):
    """check_copy.py behaviour that the clean and seeded fixture sets cannot express."""
    script = ROOT / "skills" / "copy-writer" / "scripts" / "check_copy.py"
    clean = FIXTURES / "ui-craft" / "base" / "clean" / "COPY-portfolio.md"
    page = FIXTURES / "ui-craft" / "base" / "clean" / "index.html"
    text = read(clean)
    rc, out = run_py(script, [])
    r.check("usage error: check_copy.py with no file exits 2", rc == 2, "exit %d" % rc)
    rc, out = run_py(script, ["no-such-file.md"])
    r.check("usage error: check_copy.py with a missing file exits 2", rc == 2, "exit %d" % rc)
    tmp = Path(tempfile.mkdtemp(prefix="copy-"))
    try:
        def check(name, content, *flags):
            f = tmp / name
            f.write_text(content, encoding="utf-8")
            return run_py(script, list(flags) + [f])
        literal = text.replace("Most of my work is on data-heavy tools", "I sell a climbing harness and a robust rope and a crucial knot")
        rc, out = check("words.md", literal)
        r.check("check_copy.py: hype words fail", rc == 1 and "ai-word" in out, out[-200:])
        rc, out = check("allowed.md", literal, "--allow", "harness,robust,crucial")
        r.check("check_copy.py: --allow keeps literal words", rc == 0 and "ai-word" not in out, out[-200:])
        rc, out = check("allow-line.md", literal.replace("voice: plain", "allow: harness, robust, crucial\nvoice: plain"))
        r.check("check_copy.py: allow: in the file keeps literal words", rc == 0 and "ai-word" not in out, out[-200:])
        rc, out = check("waitlist.md", text.replace("kind: portfolio", "kind: event").replace("link: Read the timetable case study", "body: Coming soon"))
        r.check("check_copy.py: 'coming soon' is allowed on an event or waitlist page", rc == 0, out[-200:])
        rc, out = check("page.html", read(page).replace("Most of my work", "We cut errors by 41%. Most of my work"), "--facts", clean)
        r.check("check_copy.py --facts: a number in the HTML must trace to the fact sheet", rc == 1 and "unsourced-number" in out, out[-200:])
        rc, out = run_py(script, ["--facts", clean, page])
        r.check("check_copy.py --facts: a clean page passes", rc == 0, out[-200:])
        rc, out = check("warn.md", text.replace("button: Email me", "button: Learn more"))
        r.check("check_copy.py: a vague button warns but passes", rc == 0 and "WARN" in out and "button" in out, out[-200:])
        rc, out = run_py(script, ["--facts", tmp / "absent.md", page])
        r.check("usage error: check_copy.py with a missing --facts file exits 2", rc == 2, "exit %d" % rc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def showcase_tests(r):
    """The showcase stays in step with the kit, and every item loads in a browser."""
    script = ROOT / "showcase" / "build_showcase.py"
    steps = read(ROOT / "skills" / "visual-qa" / "scripts" / "steps.js")
    r.check("visual-qa: phone widths use touch emulation", "Emulation.setTouchEmulationEnabled" in steps and steps.count("await setTouch(") == 4)
    rc, out = run_py(script, [])
    r.check("showcase: manifest, themes, fonts and contact sheets are current", rc == 0, out[-400:])
    manifest = json.loads(read(ROOT / "showcase" / "manifest.json"))
    tmp = Path(tempfile.mkdtemp(prefix="showcase-"))
    try:
        trimmed = tmp / "missing.json"
        trimmed.write_text(json.dumps({"items": manifest["items"][1:]}), encoding="utf-8")
        rc, out = run_py(script, ["--manifest", trimmed])
        r.check("showcase: a kit item with no manifest entry fails", rc == 1 and "no manifest entry: " + manifest["items"][0]["id"] in out, out[-300:])
        ghost = tmp / "ghost.json"
        ghost.write_text(json.dumps({"items": manifest["items"] + [{"id": "components/ghost"}]}), encoding="utf-8")
        rc, out = run_py(script, ["--manifest", ghost])
        r.check("showcase: a manifest entry with no kit item fails", rc == 1 and "components/ghost" in out, out[-300:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if not shutil.which("playwright-cli"):
        r.warn("showcase: browser test skipped", "playwright-cli is not installed")
        return
    rc, out = run_py(script, ["--verify"], timeout=600)
    if "browser step failed" in out:
        r.warn("showcase: browser test skipped", out[-200:])
    else:
        r.check("showcase: every item loads with no console errors, including long content", rc == 0, out[-500:])


def ui_craft_script_tests(r):
    """deal.py, sameness.py, preview.py, contrast.py, icons.py and audit.py."""
    scripts = ROOT / "skills" / "design-md" / "scripts"
    deal, contrast, icons, audit = scripts / "deal.py", scripts / "contrast.py", ROOT / "skills" / "ui-craft" / "scripts" / "icons.py", scripts / "audit.py"
    sameness, preview = scripts / "sameness.py", scripts / "preview.py"
    tmp = Path(tempfile.mkdtemp(prefix="craft-"))
    try:
        history = tmp / "history.json"
        def run_deal(name, has, *more):
            return run_py(deal, ["--kind", "portfolio", "--has", has, "--out", tmp / name, "--history", history] + list(more))
        rc, out = run_deal("a", "numbers,projects,experience,skills", "--seed", "1")
        made = all((tmp / "a" / n).is_file() for n in ("DESIGN.md", "design.json", "design.css"))
        r.check("deal.py: writes DESIGN.md, design.json and design.css", rc == 0 and made, out[-300:])
        rc2, out2 = run_py(contrast, [tmp / "a" / "design.css"])
        r.check("deal.py: the design.css it writes passes contrast", rc2 == 0, out2[-300:])
        rc, out = run_deal("a", "numbers,projects")
        r.check("deal.py: never overwrites an existing DESIGN.md", rc == 1 and "exists" in out, out[-200:])
        rc, out = run_deal("a", "numbers,projects", "--force", "--seed", "2")
        r.check("deal.py: --force replaces it", rc == 0, out[-200:])
        rc, out = run_deal("bare", "", "--seed", "3")
        plan = json.loads(read(tmp / "bare" / "design.json"))
        ids = [s["id"] for s in plan["sections"]]
        r.check("deal.py: no section without its material", rc == 0 and not {"projects", "experience", "skills-stack", "proof-stats", "testimonials"} & set(ids), str(ids))
        r.check("deal.py: no hero that needs missing material", plan["hero"] not in ("proof-panel", "split"), plan["hero"])
        history.write_text("[]", encoding="utf-8")
        looks = []
        for i in range(4):
            run_deal("run%d" % i, "numbers,images,projects,experience,skills", "--seed", str(i + 10))
            d = json.loads(read(tmp / ("run%d" % i) / "design.json"))
            looks.append((d["hero"], d["palette"], d["fonts"]))
        r.check("deal.py: consecutive projects get different heroes and palettes", len({x[0] for x in looks[:3]}) == 3 and len({x[1] for x in looks[:3]}) == 3, str(looks))
        rc, out = run_py(deal, ["--kind", "saas", "--out", tmp / "s", "--history", history])
        r.check("deal.py: a kind with no data fails clearly", rc == 1 and "no design data" in out, out[-200:])
        rc, out = run_py(deal, ["--kind", "portfolio", "--has", "unicorns", "--out", tmp / "s", "--history", history])
        r.check("usage error: deal.py with unknown material exits 2", rc == 2, "exit %d" % rc)

        # New options, section order and the concept file
        full = "numbers,images,portrait,projects,experience,skills,form"
        history.write_text("[]", encoding="utf-8")
        orders, seen = [], {"type_contrast": set(), "backgrounds": set(), "headings": set(), "images": set()}
        bad_order = []
        for i in range(30):
            name = "opt%d" % i
            run_deal(name, full, "--seed", str(i))
            d = json.loads(read(tmp / name / "design.json"))
            ids = [x["id"] for x in d["sections"]]
            orders.append(tuple(ids))
            for field in seen:
                seen[field].add(d[field])
            if ids[-1] != "footer" or ids[-2] != "contact" or ids[0] not in ("projects", "proof-stats", "experience"):
                bad_order.append(ids)
            if d["parallax"] and (any(x["variant"] == "timeline" for x in d["sections"]) or d["motion"] == "quiet"):
                bad_order.append(("parallax", d["parallax"]))
        r.check("deal.py: footer last, contact near the end, a strong section first, parallax within its budget", not bad_order, str(bad_order)[:300])
        r.check("deal.py: the middle of the page is shuffled", len(set(orders)) >= 10, "%d orders" % len(set(orders)))
        r.check("deal.py: every new option gets used", all(len(v) == 3 for v in seen.values()), str(seen))
        attrs = read(tmp / "opt0" / "DESIGN.md")
        r.check("deal.py: DESIGN.md lists the html attributes", all(a in attrs for a in ("data-type=", "data-bands=", "data-heads=", "data-images=")), attrs[:200])
        rc, out = run_deal("noimg", "projects,experience", "--seed", "4")
        d = json.loads(read(tmp / "noimg" / "design.json"))
        r.check("deal.py: no images, so no image treatment or parallax", rc == 0 and d["images"] == "none" and d["parallax"] is None, str(d)[:200])
        def with_concept(name, concept, has=full, *more):
            f = tmp / (name + ".json")
            f.write_text(json.dumps(concept), encoding="utf-8")
            return run_deal(name, has, "--concept", f, *more)
        concept = {"name": "Departures board", "hero": "custom", "palette": "graphite-white-cobalt", "fonts": "geist", "radius": "round", "motion": "standard", "type_contrast": "loud",
                   "backgrounds": "ruled", "headings": "side", "images": "mono", "parallax": "about", "order": ["about", "projects", "contact", "footer"],
                   "sections": {"projects": "list-rows", "about": "text-portrait"}, "signature": {"id": "flight-board", "after": "projects", "fallback": "experience/rows"}}
        before = read(history)
        rc, out = with_concept("con", concept, full, "--no-history")
        d = json.loads(read(tmp / "con" / "design.json"))
        shape = (d["hero"], d["palette"], d["fonts"], d["radius"], d["type_contrast"], d["backgrounds"], d["headings"], d["images"], d["parallax"], [x["id"] for x in d["sections"]], d["concept"])
        want = ("custom", "graphite-white-cobalt", "geist", "round", "loud", "ruled", "side", "mono", "about", ["about", "projects", "flight-board", "contact", "footer"], "Departures board")
        r.check("deal.py --concept: overrules every pick", rc == 0 and shape == want, out[-300:] + str(shape))
        r.check("deal.py --no-history: leaves the history alone", read(history) == before)
        text = read(tmp / "con" / "DESIGN.md")
        r.check("deal.py --concept: DESIGN.md names the concept, signature and parallax", "Departures board" in text and "signature, fallback `experience/rows`" in text and "| parallax |" in text, text[-900:])
        bad_concepts = {
            "material": ({"hero": "split"}, "numbers", "hero"),
            "section-material": ({"order": ["projects", "footer"]}, "numbers", "needs material"),
            "palette": ({"palette": "nope"}, full, "palette"),
            "footer": ({"order": ["about", "contact"]}, full, "end with footer"),
            "closing": ({"order": ["contact", "about", "footer"]}, full, "may follow"),
            "variant": ({"sections": {"contact": "nope"}}, full, "variant"),
            "fallback": ({"order": ["projects", "footer"], "signature": {"id": "x", "after": "hero", "fallback": "projects/list-rows"}}, full, "already on the page"),
            "parallax-images": ({"parallax": "about"}, "numbers", "needs real images"),
            "parallax-quiet": ({"motion": "quiet", "parallax": "hero", "hero": "split"}, full, "quiet"),
            "parallax-timeline": ({"motion": "standard", "hero": "split", "parallax": "hero", "sections": {"experience": "timeline"}}, full, "timeline"),
            "parallax-target": ({"motion": "standard", "parallax": "contact", "sections": {"experience": "rows"}}, full, "not an image section"),
        }
        for name, (c, has, expect) in bad_concepts.items():
            rc, out = with_concept("bad-" + name, c, has, "--history", tmp / "h2.json")
            r.check("deal.py --concept: refuses " + name, rc == 1 and expect in out and not (tmp / ("bad-" + name) / "DESIGN.md").exists(), out[-300:])
        notjson = tmp / "broken.json"
        notjson.write_text("{", encoding="utf-8")
        rc, out = run_deal("x", full, "--concept", notjson)
        r.check("usage error: deal.py with an unreadable concept exits 2", rc == 2, "exit %d" % rc)
        notjson.write_text('{"mood": "calm"}', encoding="utf-8")
        rc, out = run_deal("x", full, "--concept", notjson)
        r.check("usage error: deal.py with an unknown concept key exits 2", rc == 2, "exit %d" % rc)

        # Colour combos, the user's own colours and the role map
        colors = scripts / "colors.py"
        rc, out = run_py(colors, ["check"])
        r.check("colors.py: every combo derives a passing palette, and palettes.json is current", rc == 0, out[-300:])
        combos = json.loads(read(ROOT / "skills" / "design-md" / "assets" / "data" / "combos.json"))["combos"]
        sizes = {len(c["colors"]) for c in combos}
        audiences = {a for c in combos for a in c["audiences"]}
        r.check("colors.py: combos of 2 to 5 colours, for several audiences", sizes == {2, 3, 4, 5} and len(audiences) >= 5, str((sizes, audiences)))
        own = {"name": "Mine", "colors": {"ink": "#111111", "cream": "#F3EEE3", "orange": "#D9541E"}, "roles": {"text": "ink", "background": "cream", "action": "orange"}}
        def own_file(name, **extra):
            f = tmp / name
            f.write_text(json.dumps(dict(own, **extra)), encoding="utf-8")
            return f
        rc, out = run_py(colors, ["derive", own_file("own.json")])
        r.check("colors.py derive: keeps the user's exact values", rc == 0 and "--accent  light #D9541E" in out and "--bg  light #F3EEE3" in out and "--ink  light #111111" in out, out[:300])
        r.check("colors.py derive: a failing label becomes a CHOICE with options, not a silent swap", "CHOICE accent" in out and "shade #" in out and "large" in out and "other" in out, out[-500:])
        r.check("colors.py derive: links that fail as text become ink, underlined in the action colour", "--link  light #111111" in out and "--link-line  light #D9541E" in out, out[:900])
        rc, out = run_py(colors, ["derive", own_file("own-shade.json", decisions={"on-accent": "shade"})])
        r.check("colors.py derive: the shade decision clears the choice", rc == 0 and "CHOICE" not in out and "--accent  light #D9541E" not in out, out[-300:])
        rc, out = run_py(colors, ["near", own_file("own2.json"), "--html", tmp / "near" / "colors.html"])
        r.check("colors.py near: suggests the closest combos and writes a swatch page", rc == 0 and "ink-cream-rust" in out.split("\n")[0] and (tmp / "near" / "colors.html").is_file(), out[:300])
        rc, out = run_py(colors, ["suggest", "#D9541E", "--on", "#FFFFFF"])
        r.check("colors.py suggest: finds a passing shade of the same hue", rc == 0 and "nearest passing shade" in out, out[-200:])
        bad = own_file("bad.json", roles={"text": "ink", "background": "nope"})
        rc, out = run_py(colors, ["derive", bad])
        r.check("usage error: colors.py with a role naming a missing colour exits 2", rc == 2, "exit %d" % rc)
        pale = {"name": "Pale", "colors": {"ink": "#111111", "white": "#FFFFFF", "yellow": "#FFE066"}, "roles": {"text": "ink", "background": "white", "action": "yellow"}}
        f = tmp / "pale.json"
        f.write_text(json.dumps(pale), encoding="utf-8")
        rc, out = run_py(colors, ["derive", f])
        r.check("colors.py derive: a pale yellow cannot be a button on white", rc == 1 and "needs 3:1" in out, out[-300:])
        rc, out = run_deal("own", full, "--colors", own_file("own3.json"), "--seed", "5")
        text = read(tmp / "own" / "DESIGN.md") if rc == 0 else ""
        r.check("deal.py --colors: role map with uses, the user's values, and the open choice", rc == 0 and "| `--accent` | `#D9541E`" in text and "Primary button label" in text and "Open colour choices" in text and "CHOICE" in out, out[-300:])
        rc, out = run_deal("large", full, "--colors", own_file("own4.json", decisions={"on-accent": "large"}), "--seed", "6")
        css_text = read(tmp / "large" / "design.css") if rc == 0 else ""
        rc2, out2 = run_py(contrast, [tmp / "large" / "design.css"]) if rc == 0 else (1, out)
        r.check("deal.py --colors: large labels are written and pass at 3:1", rc == 0 and ".btn--primary { font-size: var(--text-h3); font-weight: 700; }" in css_text and rc2 == 0, out2[-300:])
        rc, out = run_deal("aud", "numbers,projects", "--audience", "local", "--seed", "7")
        d = json.loads(read(tmp / "aud" / "design.json")) if rc == 0 else {}
        local = {c["id"] for c in combos if "local" in c["audiences"] and "portfolio" in c["kinds"]}
        r.check("deal.py --audience: picks a combo made for that audience", d.get("palette") in local, str(d.get("palette")))
        rc, out = with_concept("two", dict(concept, palette="navy-snow-cobalt-sky-ember", two_actions=True, order=["about", "projects", "contact", "footer"], signature=None, parallax=None), full, "--no-history")
        r.check("deal.py: two distinct actions allow the combo's second button colour", rc == 0 and ".btn--accent-2" in read(tmp / "two" / "DESIGN.md"), out[-300:])

        # sameness.py
        hist = tmp / "same.json"
        hist.write_text("[]", encoding="utf-8")
        run_deal("s1", full, "--seed", "1", "--history", hist)
        design = tmp / "s1" / "design.json"
        rc, out = run_py(sameness, [design, "--history", hist])
        r.check("sameness.py: ignores its own entry in the history", rc == 0 and "no earlier" in out, out[-200:])
        entries = json.loads(read(hist))
        twin = dict(entries[0], run="other", at="2026-01-01T00:00:00Z")
        hist.write_text(json.dumps([twin] + entries), encoding="utf-8")
        rc, out = run_py(sameness, [design, "--history", hist])
        r.check("sameness.py: an identical structure warns", rc == 0 and "WARN 100%" in out and "RESULT  WARN" in out, out[-200:])
        other = dict(twin, hero="zzz", order=["a", "b"], shapes=["c", "d"], type_contrast="zzz", backgrounds="zzz", headings="zzz", images="zzz")
        hist.write_text(json.dumps([other] + entries), encoding="utf-8")
        rc, out = run_py(sameness, [design, "--history", hist])
        r.check("sameness.py: a different structure passes", rc == 0 and "RESULT  PASS" in out, out[-200:])
        custom = json.loads(read(design))
        custom["hero"] = "custom"
        custom_file = tmp / "custom.json"
        custom_file.write_text(json.dumps(custom), encoding="utf-8")
        hist.write_text(json.dumps([dict(twin, hero="custom")] + entries), encoding="utf-8")
        rc, out = run_py(sameness, [custom_file, "--history", hist, "--threshold", "0.99"])
        r.check("sameness.py: two custom heroes are not a repeat", "RESULT  PASS" in out, out[-200:])
        hist.write_text(json.dumps([{"hero": "x", "palette": "y"}]), encoding="utf-8")
        rc, out = run_py(sameness, [design, "--history", hist])
        r.check("sameness.py: skips old entries with no structure", "no earlier" in out, out[-200:])
        rc, out = run_py(sameness, [tmp / "absent.json"])
        r.check("usage error: sameness.py with a missing file exits 2", rc == 2, "exit %d" % rc)
        rc, out = run_py(sameness, [design, "--threshold", "7"])
        r.check("usage error: sameness.py with a bad threshold exits 2", rc == 2, "exit %d" % rc)

        # preview.py, with a stand-in for the browser
        site = tmp / "previews"
        site.mkdir()
        for n in "abc":
            (site / (n + ".html")).write_text("<h1>x</h1>", encoding="utf-8")
        fake = "python3 -I " + str(FIXTURES / "ui-craft" / "preview" / "fake_cli.py")
        rc, out = run_py(preview, ["--dir", site, "--names", "a,b,c", "--cli", fake])
        shots = sorted(f.name for f in (site / "shots").glob("*.png"))
        r.check("preview.py: saves each preview at both widths", rc == 0 and shots == sorted("%s-%d.png" % (n, w) for n in "abc" for w in (1440, 390)), out[-300:] + str(shots))
        log = read(site / "shots" / ".browser" / "cli.log")
        r.check("preview.py: visible browser, its own session, closed at the end", "--headed" in log and log.startswith("-s=ui-craft-preview-") and log.strip().splitlines()[-1].endswith("close"), log[:200])
        r.check("preview.py: serves only on this machine", "http://127.0.0.1:" in log, log[:300])
        os.environ["FAKE_CLI_FAIL"] = "goto"
        try:
            rc, out = run_py(preview, ["--dir", site, "--names", "a", "--cli", fake])
        finally:
            del os.environ["FAKE_CLI_FAIL"]
        r.check("preview.py: a browser failure reports FAIL and still closes", rc == 1 and "FAIL goto failed" in out and read(site / "shots" / ".browser" / "cli.log").strip().splitlines()[-1].endswith("close"), out[-200:])
        rc, out = run_py(preview, ["--dir", site, "--names", "zzz", "--cli", fake])
        r.check("usage error: preview.py with a missing preview exits 2", rc == 2, "exit %d" % rc)
        rc, out = run_py(preview, ["--dir", site, "--names", "../a", "--cli", fake])
        r.check("usage error: preview.py refuses a path as a name", rc == 2, "exit %d" % rc)

        low = tmp / "low.css"
        low.write_text(re.sub(r"--ink-2: [^;]+;", "--ink-2: oklch(80% 0.01 90);", read(tmp / "a" / "design.css"), count=1), encoding="utf-8")
        rc, out = run_py(contrast, [low])
        r.check("contrast.py: pale text fails", rc == 1 and "--ink-2 on --bg" in out, out[-300:])
        rc, out = run_py(contrast, [])
        r.check("usage error: contrast.py with no file exits 2", rc == 2, "exit %d" % rc)

        src = tmp / "tabler"
        src.mkdir()
        (src / "star.svg").write_text("<!-- tags -->\n<svg></svg>\n", encoding="utf-8")
        page = tmp / "page.html"
        page.write_text('<i data-icon="star"></i><i data-icon="brand-postgresql"></i>', encoding="utf-8")
        rc, out = run_py(icons, ["--out", tmp / "ic", "--base", src.as_uri(), page])
        r.check("icons.py: copies what exists, without its comment", rc == 0 and read(tmp / "ic" / "star.svg").startswith("<svg"), out[-300:])
        r.check("icons.py: lists what is missing, and draws nothing", "MISSING brand-postgresql" in out and not (tmp / "ic" / "brand-postgresql.svg").exists(), out[-300:])
        rc, out = run_py(icons, ["--out", tmp / "ic", "--names", "../evil"])
        r.check("usage error: icons.py refuses a path as a name", rc == 2, "exit %d" % rc)

        bad = {
            "a.css": (".x { color: #ff0000; }", "raw-colour"), "b.css": (".x { transition: all 200ms; }", "transition-all"),
            "c.css": (".x { transition: width 200ms; }", "layout-animation"), "d.css": (".x { outline: none; }", "outline-removed"),
            "e.html": ('<div style="margin:0"></div>', "inline-style"), "f.html": ('<img src="a.png" width="1" height="1">', "img-alt"),
            "g.html": ('<img src="a.png" alt="x">', "img-size"),
            "h.html": ('<div data-parallax><h2>Hello</h2><img src="a.png" alt="x" width="1" height="1"></div>', "parallax-text"),
            "i.html": ('<div data-parallax><img src="a.png" alt="x" width="1" height="1"> Hello</div>', "parallax-text"),
            "j.html": ('<div data-parallax></div>', "parallax-no-image"),
            "k.html": ('<img data-parallax src="a.png" alt="x" width="1" height="1">', "parallax-frame"),
            "l.html": ('<div data-parallax><img src="a.png" alt="x" width="1" height="1"></div><ol data-timeline></ol>', "scroll-linked"),
            "m.html": ('<h1 data-parallax>Moving words</h1>', "parallax-text"),
        }
        for name, (content, cid) in bad.items():
            f = tmp / name
            f.write_text(content, encoding="utf-8")
            rc, out = run_py(audit, [f])
            r.check("audit.py: catches " + cid, rc == 1 and cid in out, out[-200:])
        ok = tmp / "ok.css"
        ok.write_text(".x { color: var(--ink); outline: none; } /* audit:ok ring on parent */\n", encoding="utf-8")
        r.check("audit.py: audit:ok skips a line", run_py(audit, [ok])[0] == 0)
        ok = tmp / "ok.html"
        ok.write_text('<div class="frame" data-parallax><div><img src="a.png" alt="x" width="1" height="1"></div></div><p>Words after the frame</p>', encoding="utf-8")
        r.check("audit.py: a good parallax frame passes", run_py(audit, [ok])[0] == 0)
        rc, out = run_py(audit, [])
        r.check("usage error: audit.py with no file exits 2", rc == 2, "exit %d" % rc)

        if shutil.which("node"):
            for js in ("motion.js", "theme.js"):
                copy = tmp / (js + ".mjs")
                copy.write_text(read(ROOT / "skills" / "ui-craft" / "assets" / "kit" / "motion" / js), encoding="utf-8")
                p = subprocess.run(["node", "--check", str(copy)], capture_output=True, text=True)
                r.check("kit script parses: " + js, p.returncode == 0, p.stderr[-300:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def visual_qa_tests(r):
    """capture.py against a stand-in for playwright-cli, report.py against a real capture."""
    scripts = ROOT / "skills" / "visual-qa" / "scripts"
    capture, report = scripts / "capture.py", scripts / "report.py"
    fx = FIXTURES / "visual-qa"
    fake = " ".join([sys.executable, "-I", "-B", str(fx / "fake_cli.py")])
    tmp = Path(tempfile.mkdtemp(prefix="visual-qa-"))
    try:
        # capture.py: a local site, with one route that has no dark theme and one that fails
        out = tmp / "local"
        rc, text = run_py(capture, ["--url", "http://localhost:3000", "--out", out, "--viewports", "390x844", "--cli", fake])
        r.check("capture.py: a step that fails is reported and ends in RESULT FAIL", rc == 1 and "RESULT  FAIL" in text and "broken" in text, "exit %d: %s" % (rc, text[-300:]))
        data = json.loads(read(out / "results.json"))
        log = read(out / "cli.log")
        ids = [s["id"] for s in data["shots"]]
        r.check("capture.py: light and dark shots, with the dark shot of a route with no dark theme dropped", ids == ["home-390-light", "home-390-dark", "about-390-light"], str(ids))
        r.check("capture.py: says which route has no dark theme", any("/about" in n and "dark" in n for n in data["notes"]), str(data["notes"]))
        r.check("capture.py: writes tiles and full-page images", (out / "tiles" / "home-390-dark-02.jpg").is_file() and (out / "full" / "home-390-dark.png").is_file())
        r.check("capture.py: opens a visible browser", re.search(r"open about:blank --headed", log) is not None, log[:200])
        r.check("capture.py: closes the browser even after a failed step", log.strip().splitlines()[-1].endswith("close"), log[-200:])
        r.check("capture.py: uses its own session, not the user's", all(ln.startswith(("-s=visual-qa-", "--version")) for ln in log.strip().splitlines()), log[:200])
        merged = data["route_findings"]["/"]
        r.check("capture.py: repeated findings are merged", len(merged) == 1 and merged[0]["count"] == 2 and merged[0]["samples"] == ["a", "b"], str(merged))
        r.check("capture.py: the phone menu image is saved", any((out / x["image"]).is_file() for x in data["extras"]), str(data["extras"]))
        r.check("capture.py: Chromium is configured", "chromium" in read(out / ".playwright" / "cli.config.json"))
        r.check("capture.py: leaves no step file behind", not (out / ".step.js").exists())

        # capture.py: not a local site
        out = tmp / "remote"
        rc, text = run_py(capture, ["--url", "https://example.org", "--out", out, "--routes", "/", "--viewports", "390x844", "--themes", "light", "--cli", fake])
        data = json.loads(read(out / "results.json"))
        r.check("capture.py: a remote site runs clean", rc == 0 and "RESULT  PASS" in text, "exit %d: %s" % (rc, text[-300:]))
        r.check("capture.py: no clicking or submitting on a remote site", '"step": "interact"' not in read(out / "cli.log") and not data["run"]["interactions"] and data["notes"], str(data["notes"]))
        rc, text = run_py(capture, ["--url", "https://example.org", "--out", tmp / "allowed", "--routes", "/", "--viewports", "390x844", "--themes", "light", "--allow-remote", "--cli", fake])
        r.check("capture.py: --allow-remote turns interactions on", rc == 0 and json.loads(read(tmp / "allowed" / "results.json"))["run"]["interactions"], text[-200:])

        # capture.py: refusals
        rc, text = run_py(capture, ["--url", "http://localhost:3000", "--out", out, "--cli", fake])
        r.check("capture.py: refuses a folder that already has files", rc == 1 and "already has files" in text, "exit %d" % rc)
        rc, text = run_py(capture, ["--url", "http://localhost:3000", "--out", tmp / "badview", "--viewports", "wide", "--cli", fake])
        r.check("usage error: capture.py with a bad viewport exits 2", rc == 2, "exit %d: %s" % (rc, text[-200:]))
        rc, text = run_py(capture, ["--url", "http://localhost:3000", "--out", tmp / "nocli", "--cli", "no-such-playwright-cli"])
        r.check("capture.py: a missing CLI says how to install it", rc == 1 and "npm install -g @playwright/cli" in text, "exit %d: %s" % (rc, text[-200:]))

        # The JavaScript parses, joined the way capture.py joins it
        if shutil.which("node"):
            joined = tmp / "joined.js"
            joined.write_text("async page => {\nconst CONFIG = {};\nconst PAGE_CHECKS = %s;\n%s\n}\n" % (read(scripts / "page_checks.js").strip(), read(scripts / "steps.js")), encoding="utf-8")
            p = subprocess.run(["node", "--check", str(joined)], capture_output=True, text=True)
            r.check("page_checks.js and steps.js parse", p.returncode == 0, p.stderr[-300:])
        else:
            r.warn("page_checks.js and steps.js parse", "node is not installed; not checked")

        # report.py
        run = tmp / "run"
        shutil.copytree(fx / "capture", run)
        rc, text = run_py(report, ["--run", run])
        r.check("report.py: no grades.json fails", rc == 1 and "grades.json" in text, "exit %d" % rc)
        rc, text = run_py(report, ["--run", run, "--skeleton"])
        blank = json.loads(read(run / "grades.json"))
        r.check("report.py --skeleton: one entry per shot and seven areas", rc == 0 and len(blank["shots"]) == 4 and len(blank["shots"]["home-390-light"]) == 7, text[-200:])
        rc, text = run_py(report, ["--run", run, "--skeleton"])
        r.check("report.py --skeleton: never overwrites grades", rc == 1 and "already exists" in text, "exit %d" % rc)
        rc, text = run_py(report, ["--run", run])
        r.check("report.py: blank grades fail", rc == 1 and "has grade '?'" in text and "summary is empty" in text and "top_fixes" in text, "exit %d: %s" % (rc, text[-200:]))

        good = json.loads(read(fx / "grades-good.json"))
        missing = json.loads(json.dumps(good))
        del missing["shots"]["about-html-390-light"]
        (run / "grades.json").write_text(json.dumps(missing), encoding="utf-8")
        rc, text = run_py(report, ["--run", run])
        r.check("report.py: a shot with no grades fails", rc == 1 and "no grades for shot about-html-390-light" in text, "exit %d: %s" % (rc, text[-200:]))

        high = json.loads(json.dumps(good))
        for area in high["shots"]["home-390-light"]:
            high["shots"]["home-390-light"][area]["grade"] = "A"
        (run / "grades.json").write_text(json.dumps(high), encoding="utf-8")
        results = json.loads(read(run / "results.json"))
        results["shots"][0]["findings"][0]["samples"] = ["</script><img src=x onerror=alert(1)>"]
        (run / "results.json").write_text(json.dumps(results), encoding="utf-8")
        rc, text = run_py(report, ["--run", run])
        r.check("report.py: complete grades build the report", rc == 0 and "RESULT  PASS" in text and (run / "report.html").is_file() and (run / "summary.md").is_file(), "exit %d: %s" % (rc, text[-300:]))
        html = read(run / "report.html")
        r.check("report.py: page text cannot close the script block", "</script><img" not in html and "__REPORT_DATA__" not in html)
        m = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S)
        shot = next(s for s in json.loads(m.group(1))["shots"] if s["id"] == "home-390-light")
        layout, spacing, motion = shot["areas"]["layout"], shot["areas"]["spacing"], shot["areas"]["motion"]
        r.check("report.py: a measured fault lowers the grade and says so", layout["grade"] == "C" and layout["capped_from"] == "A" and "margins" in layout["capped_by"] and spacing["grade"] == "C", str(layout))
        r.check("report.py: motion comes from the measurements", motion["grade"] == "D" and "hidden-content" in motion["reason"], str(motion))
        r.check("report.py: images are embedded", "data:image/jpeg;base64," in html)
        rc, text = run_py(report, ["--run", tmp / "no-such-folder"])
        r.check("usage error: report.py with no folder exits 2", rc == 2, "exit %d" % rc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def engine_tests(r):
    """Orchestrator engine: route validation, then a whole project run in a temporary copy."""
    engine = ROOT / "skills" / "orchestrator" / "scripts" / "engine.py"
    fx = FIXTURES / "orchestrator"
    if not r.check("engine fixtures exist", fx.is_dir() and engine.is_file(), "tests/fixtures/orchestrator or engine.py is missing"):
        return

    def eng(work, *args):
        rc, out = run_py(engine, list(args) + ["--root", work, "--dir", Path(work) / ".orchestrator"])
        return rc, out

    def as_json(out):
        try:
            return json.loads(out)
        except ValueError:
            return {}

    tmp = Path(tempfile.mkdtemp(prefix="engine-"))
    try:
        # Route validation, one rule at a time
        for name in sorted(ENGINE_BAD_ROUTES):
            d = tmp / name
            (d / ".orchestrator").mkdir(parents=True)
            shutil.copy(fx / "routes" / (name + ".json"), d / ".orchestrator" / "route.json")
            rc, out = eng(d, "validate", "--no-docs")
            fails = [ln for ln in out.splitlines() if ln.startswith("FAIL")]
            hit = [ln for ln in fails if re.search(ENGINE_BAD_ROUTES[name], ln)]
            r.check("engine validate refuses %s" % name, rc == 1 and bool(hit) and len(fails) == len(hit),
                    "exit %d: %s" % (rc, re.sub(r"\s+", " ", out)[:200]))
        d = tmp / "good-route"
        (d / ".orchestrator").mkdir(parents=True)
        shutil.copy(fx / "routes" / "good-route.json", d / ".orchestrator" / "route.json")
        rc, out = eng(d, "validate", "--no-docs")
        r.check("engine validate accepts good-route", rc == 0 and "RESULT  PASS" in out, out.strip()[-200:])
        d = tmp / "good-design-route"
        (d / ".orchestrator").mkdir(parents=True)
        shutil.copy(fx / "routes" / "good-design-route.json", d / ".orchestrator" / "route.json")
        rc, out = eng(d, "validate", "--no-docs")
        r.check("engine validate accepts a two-skill design phase", rc == 0 and "RESULT  PASS" in out, out.strip()[-200:])
        # Gate C: design-md may not start, or be merged, before COPY.md is approved
        (d / "spec.approved.md").write_text("spec\n")
        (d / "phases").mkdir()
        for n in ("1", "2"):
            (d / "phases" / ("phase-%s.md" % n)).write_text("phase\n")
        eng(d, "init")
        eng(d, "approve", "gate-a")
        eng(d, "approve", "gate-b")
        rc, out = eng(d, "next")
        parked = as_json(out).get("parked", [{}])
        r.check("engine gate C: the design phase is blocked before approval",
                rc == 0 and parked[0].get("blocked_by") == "gate-c"
                and parked[0].get("main_session_skills") == ["ai-toolkit:copy-writer", "ai-toolkit:design-md"], out[:300])
        rc, out = eng(d, "approve", "gate-c")
        r.check("engine gate C: approving without COPY.md is refused", rc == 1 and "copy-writer" in out, out.strip()[-200:])
        (d / "COPY.md").write_text("kind: portfolio\n")
        rc, out = eng(d, "approve", "gate-c")
        r.check("engine gate C: approval of COPY.md is recorded", rc == 0, out.strip()[-200:])
        rc, out = eng(d, "next")
        r.check("engine gate C: the design phase is open after approval",
                "blocked_by" not in as_json(out).get("parked", [{}])[0], out[:300])
        (d / "COPY.md").write_text("kind: portfolio\nedited\n")
        rc, out = eng(d, "merge", "p1")
        r.check("engine gate C: merge is refused after COPY.md changed", rc == 1 and "Gate C" in out, out.strip()[-200:])
        eng(d, "approve", "gate-c")
        rc, out = eng(d, "merge", "p1")
        r.check("engine gate C: merge works once approved again", rc == 0, out.strip()[-200:])
        rc, out = eng(d, "status")
        r.check("engine gate C: status shows it", "Gate C: approved" in out, out[-200:])

        # A whole project
        w = tmp / "project"
        shutil.copytree(fx / "project", w)
        (w / ".orchestrator").mkdir()
        shutil.move(str(w / "route.json"), str(w / ".orchestrator" / "route.json"))
        rep = lambda name: str(fx / "reports" / name)

        def step(label, ok, detail=""):
            return r.check("engine lifecycle: " + label, ok, detail)

        rc, out = eng(w, "validate")
        if not step("validate passes with the phase documents present", rc == 0, out.strip()[-200:]):
            return
        rc, out = eng(w, "next")
        step("next before init is refused", rc == 1 and "init" in out)
        rc, out = eng(w, "init")
        step("init creates the ledger", rc == 0, out.strip()[-200:])
        rc, out = eng(w, "init")
        step("init a second time is refused", rc == 1)
        rc, out = eng(w, "next")
        step("next before Gate A is refused", rc == 1 and "Gate A" in out, out.strip()[-200:])
        eng(w, "approve", "gate-a")
        rc, out = eng(w, "next")
        step("next before Gate B is refused", rc == 1 and "Gate B" in out, out.strip()[-200:])
        rc, out = eng(w, "approve", "gate-b")
        step("Gate B is recorded", rc == 0, out.strip()[-200:])
        rc, out = eng(w, "next")
        data = as_json(out)
        step("next releases only p1", rc == 0 and [x["id"] for x in data.get("ready", [])] == ["p1"], out[:300])
        rc, out = eng(w, "start", "p2")
        step("start p2 is refused while p1 is unmerged", rc == 1 and "waiting for p1" in out, out.strip()[-200:])
        rc, out = eng(w, "start", "p1")
        started = as_json(out).get("started", [{}])[0]
        step("start p1 returns a runner call with an absolute run directory",
             rc == 0 and started.get("agent") == "ai-toolkit:skill-runner" and Path(started.get("run_dir", "x")).is_absolute()
             and started.get("run_dir", "").endswith("p1-1") and len(started.get("inputs", [])) == 2, out[:300])
        rc, out = eng(w, "record", "p1", rep("blocked"))
        step("a blocked report fails the phase", rc == 1 and "blocked" in out, out.strip()[-200:])
        rc, out = eng(w, "next")
        halted = {x["id"] for x in as_json(out).get("halted", [])}
        step("failing p1 halts everything behind it", halted == {"p2", "p3", "p4", "p5", "p6", "p7", "p8"}, out[:300])
        eng(w, "retry", "p1")
        rc, out = eng(w, "start", "p1")
        step("a retry gets a new run directory", rc == 0 and as_json(out)["started"][0]["run_dir"].endswith("p1-2"), out[:300])
        for bad, why in (("no-evidence", "evidence"), ("running", "running"), ("empty", "does not exist")):
            eng(w, "retry", "p1")
            eng(w, "start", "p1")
            rc, out = eng(w, "record", "p1", rep(bad))
            step("a report that is '%s' fails the phase" % bad, rc == 1 and why in out, out.strip()[-200:])
        eng(w, "retry", "p1")
        eng(w, "start", "p1")
        rc, out = eng(w, "record", "p1", rep("done"), "--tokens", "1234")
        step("a report with status and evidence builds the phase", rc == 0, out.strip()[-200:])
        rc, out = eng(w, "pushed", "p1", "phase-1-skeleton")
        step("the pushed branch of a built phase is recorded", rc == 0, out.strip()[-200:])
        rc, out = eng(w, "status")
        step("status shows the pushed branch", rc == 0 and "pushed: phase-1-skeleton" in out, out.strip()[-300:])
        rc, out = eng(w, "pushed", "p2", "phase-2")
        step("a push for a phase that is not built is refused", rc == 1, out.strip()[-200:])
        rc, out = eng(w, "next")
        held = {x["id"]: x["why"] for x in as_json(out).get("held", [])}
        step("a built phase does not release p2 until it is merged", held.get("p2") == "waiting for p1", out[:300])
        rc, out = eng(w, "merge", "p1")
        step("merge p1", rc == 0, out.strip()[-200:])
        rc, out = eng(w, "merge", "p2")
        step("merge of a pending phase is refused", rc == 1)
        eng(w, "start", "p2")
        eng(w, "record", "p2", rep("done"))
        eng(w, "merge", "p2")
        rc, out = eng(w, "start", "p3")
        eng(w, "retry", "p3")
        rc, out = eng(w, "record", "p3", rep("done"))
        step("record of a phase that is not running is refused", rc == 1 and "not running" in out, out.strip()[-200:])
        eng(w, "start", "p3")
        rc, out = eng(w, "record", "p3", rep("done"))
        step("a two-skill phase with a one-skill report fails", rc == 1 and "skill(s)" in out, out.strip()[-200:])
        eng(w, "retry", "p3")
        eng(w, "start", "p3")
        rc, out = eng(w, "record", "p3", rep("done-two"))
        step("a two-skill report builds a two-skill phase", rc == 0, out.strip()[-200:])
        eng(w, "merge", "p3")
        rc, out = eng(w, "next")
        data = as_json(out)
        ready = [x["id"] for x in data.get("ready", [])]
        held = {x["id"]: x["why"] for x in data.get("held", [])}
        step("the worker cap of 2 releases p4 and p5 and holds p6", ready == ["p4", "p5"] and "worker cap" in held.get("p6", ""), out[:400])
        rc, out = eng(w, "start", "p4", "p5", "p6")
        step("start refuses a third phase over the cap and starts nothing", rc == 1 and "p6 may not start" in out, out.strip()[-200:])
        rc, out = eng(w, "status")
        step("a refused start leaves p4 pending", [ln.split()[1] for ln in out.splitlines() if ln.startswith("p4 ")] == ["pending"], out[:300])
        eng(w, "start", "p4", "p5")
        # tampering with the route after Gate B stops everything
        route_file = w / ".orchestrator" / "route.json"
        text = read(route_file)
        route_file.write_text(text.replace('"max_parallel": 2', '"max_parallel": 3'))
        rc, out = eng(w, "next")
        step("a route changed after Gate B is refused", rc == 1 and "route changed" in out, out.strip()[-200:])
        route_file.write_text(text)
        eng(w, "record", "p4", rep("done"))
        eng(w, "merge", "p4")
        rc, out = eng(w, "next")
        ready = [x["id"] for x in as_json(out).get("ready", [])]
        step("p6 is released once a worker is free", ready == ["p6"], out[:300])
        eng(w, "start", "p6")
        eng(w, "record", "p5", rep("done"))
        eng(w, "record", "p6", rep("done"))
        eng(w, "merge", "p5")
        eng(w, "merge", "p6")
        rc, out = eng(w, "next")
        step("p7 is released after p4, p5 and p6 merge", [x["id"] for x in as_json(out).get("ready", [])] == ["p7"], out[:300])
        eng(w, "start", "p7")
        eng(w, "record", "p7", rep("done"))
        eng(w, "merge", "p7")
        rc, out = eng(w, "next")
        data = as_json(out)
        step("the parked phase is listed for the user, not released to a helper",
             [x["id"] for x in data.get("parked", [])] == ["p8"] and not data.get("ready") and not data.get("done"), out[:300])
        step("a parked entry carries main_session_skill", all("main_session_skill" in x for x in data.get("parked", [])), out[:300])
        rc, out = eng(w, "start", "p8")
        step("start refuses a parked phase", rc == 1 and "parked for you" in out, out.strip()[-200:])
        rc, out = eng(w, "merge", "p8")
        step("the user's finished step marks the parked phase merged", rc == 0, out.strip()[-200:])
        rc, out = eng(w, "next")
        step("next reports done when every phase is merged", as_json(out).get("done") is True, out[:200])
        events = json.loads(read(w / ".orchestrator" / "state.json")).get("events", [])
        step("the ledger logged every command", len(events) > 30, "%d events" % len(events))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- cases


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_transcript(text):
    tool_uses, final, last_text = [], None, ""
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "assistant":
            content = (ev.get("message") or {}).get("content") or []
            for block in content if isinstance(content, list) else []:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use":
                    tool_uses.append((block.get("name") or "", block.get("input") or {}))
                elif block.get("type") == "text" and block.get("text"):
                    last_text = block["text"]
        elif ev.get("type") == "result":
            final = ev
    output = final["result"] if final and isinstance(final.get("result"), str) else last_text
    return tool_uses, final, output


def evaluate(case, work, before, tool_uses, final, output):
    fails = []
    if final is None:
        fails.append("no result event in the transcript (the run died or printed no JSON)")
    elif final.get("is_error"):
        fails.append("claude reported an error: %s" % str(final.get("result"))[:200])

    skills_called = [str(i.get("skill") or i.get("name") or "") for n, i in tool_uses if n == "Skill"]
    for s in case.get("skills", []):
        if not any(x == s or x.endswith(":" + s) for x in skills_called):
            fails.append("Skill call missing: %s (called: %s)" % (s, ", ".join(skills_called) or "none"))
    agents_called = [str(i.get("subagent_type") or i.get("description") or "") for n, i in tool_uses if n in ("Agent", "Task")]
    for a in case.get("agents", []):
        if not any(re.search(a, x) for x in agents_called):
            fails.append("Agent call missing: %s (called: %s)" % (a, ", ".join(agents_called) or "none"))
    read_paths = []
    for n, i in tool_uses:
        if n == "Read":
            read_paths.append(str(i.get("file_path") or ""))
        elif n == "Bash":
            read_paths.append(str(i.get("command") or ""))
    for rx in case.get("reads", []):
        if not any(re.search(rx, p) for p in read_paths):
            fails.append("file was not read: /%s/" % rx)

    for rx in case.get("must", []):
        if not re.search(rx, output, re.M):
            fails.append("output does not match /%s/" % rx)
    for rx in case.get("must_not", []):
        if re.search(rx, output, re.M):
            fails.append("output matches forbidden /%s/" % rx)

    for spec in case.get("files", []):
        pattern = spec["glob"] if isinstance(spec, dict) else spec
        spec = spec if isinstance(spec, dict) else {}
        hits = sorted(glob.glob(str(work / pattern), recursive=True))
        hits = [h for h in hits if Path(h).is_file()]
        if spec.get("exists", True):
            if not hits:
                fails.append("no file matches %s" % pattern)
                continue
        elif hits:
            fails.append("file should not exist: %s" % Path(hits[0]).relative_to(work).as_posix())
            continue
        body = "\n".join(read(h) for h in hits)
        if spec.get("each"):
            for h in hits:
                for rx in spec.get("must", []):
                    if not re.search(rx, read(h), re.M):
                        fails.append("%s does not match /%s/" % (Path(h).relative_to(work).as_posix(), rx))
        else:
            for rx in spec.get("must", []):
                if not re.search(rx, body, re.M):
                    fails.append("%s does not match /%s/" % (pattern, rx))
        for rx in spec.get("must_not", []):
            if re.search(rx, body, re.M):
                fails.append("%s matches forbidden /%s/" % (pattern, rx))
    for pattern in case.get("no_files", []):
        hits = [h for h in glob.glob(str(work / pattern), recursive=True)]
        if hits:
            fails.append("file should not exist: %s" % Path(hits[0]).relative_to(work).as_posix())
    for name, digest in before.items():
        p = work / name
        if not p.is_file() or sha(p) != digest:
            fails.append("file changed or removed: %s" % name)
    for cmd in case.get("post", []):
        p = subprocess.run(["bash", "-c", cmd.replace("{repo}", str(ROOT))], cwd=str(work), capture_output=True, text=True, timeout=180)
        if p.returncode != 0:
            fails.append("post command failed (exit %d): %s %s" % (p.returncode, cmd, (p.stdout + p.stderr).strip()[:200]))
    return fails


def execute(case, attempt):
    """Run one case once. Returns a dict with passed, failures, seconds."""
    cid = case["id"]
    tmp = Path(tempfile.mkdtemp(prefix="case-%s-" % cid))
    work = tmp / "work"
    started = time.time()
    try:
        shutil.copytree(FIXTURES / case["fixture"], work)
        before = {name: sha(work / name) for name in case.get("unchanged", []) if (work / name).is_file()}
        cmd = [
            "claude", "-p", case["prompt"],
            "--plugin-dir", str(ROOT),
            "--add-dir", str(ROOT),
            "--permission-mode", "dontAsk",
            "--allowedTools", case.get("tools", DEFAULT_TOOLS),
            "--output-format", "stream-json",
            "--verbose",
        ]
        try:
            p = subprocess.run(cmd, cwd=str(work), capture_output=True, text=True, stdin=subprocess.DEVNULL,
                               timeout=case.get("timeout", 900))
            stdout, stderr, timed_out = p.stdout, p.stderr, False
        except subprocess.TimeoutExpired as e:
            stdout = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
            stderr, timed_out = "", True
        (RUNS / ".cases").mkdir(parents=True, exist_ok=True)
        (RUNS / ".cases" / ("%s-%d.jsonl" % (cid, attempt))).write_text(stdout + ("\n" + stderr if stderr else ""), encoding="utf-8")
        tool_uses, final, output = parse_transcript(stdout)
        if timed_out:
            fails = ["timed out after %ss" % case.get("timeout", 900)]
        else:
            fails = evaluate(case, work, before, tool_uses, final, output)
        return {"id": cid, "attempt": attempt, "passed": not fails, "failures": fails, "seconds": time.time() - started}
    except Exception as e:  # keep one broken case from stopping the run
        return {"id": cid, "attempt": attempt, "passed": False, "failures": ["runner error: %r" % (e,)], "seconds": time.time() - started}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run_with_retry(case, retry):
    attempts = [execute(case, 1)]
    if not attempts[0]["passed"] and retry:
        attempts.append(execute(case, 2))
    return case, attempts


def select(cases, args):
    if args.case:
        known = {c["id"] for c in cases}
        unknown = [i for i in args.case if i not in known]
        return [c for c in cases if c["id"] in args.case], unknown
    tiers = {"fast": {"fast"}, "slow": {"fast", "slow"}, "network": {"network"}}[args.tier]
    return [c for c in cases if c.get("tier") in tiers], []


def cmd_cases(args):
    cases, errors = load_cases()
    if errors:
        for e in errors:
            print("FAIL    case files: " + e)
        print("RESULT  FAIL")
        return 1
    if args.list:
        for c in cases:
            print("%-34s %-8s %s" % (c["id"], c["tier"], c["source"]))
        print("%d cases" % len(cases))
        return 0

    r = Report()
    if not shutil.which("claude"):
        r.fail("claude CLI is on PATH")
        return r.finish()
    chosen, unknown = select(cases, args)
    if unknown:
        r.fail("case ids exist", "unknown: " + ", ".join(unknown))
        return r.finish()
    if not chosen:
        r.fail("cases selected", "no case matches")
        return r.finish()

    version = json.loads(read(ROOT / ".claude-plugin" / "plugin.json")).get("version", "unknown")
    started = time.time()
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        futures = [pool.submit(run_with_retry, c, not args.no_retry) for c in chosen]
        for fut in concurrent.futures.as_completed(futures):
            case, attempts = fut.result()
            results[case["id"]] = attempts
            last = attempts[-1]
            for a in attempts[:-1]:
                r.note("RETRY", case["id"], "attempt %d failed: %s" % (a["attempt"], "; ".join(a["failures"])[:300]))
            secs = sum(a["seconds"] for a in attempts)
            if last["passed"]:
                r.ok("%s (%s, %ds)" % (case["id"], case["tier"], secs))
            else:
                r.fail("%s (%s, %ds)" % (case["id"], case["tier"], secs), "; ".join(last["failures"])[:600])
    wall = time.time() - started

    if not args.no_log and not args.case:
        log = Path(args.log) if args.log else RUNS / ("model-cases-%s.md" % version)
        write_log(log, chosen, results, version, args, wall)
        print("log     " + rel(log))
    print("elapsed %ds with %d job(s)" % (wall, args.jobs))
    return r.finish()


def write_log(path, chosen, results, version, args, wall):
    claude_version = ""
    try:
        claude_version = subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    lines = [
        "# Model-run cases: ai-toolkit %s" % version,
        "",
        "- Date: %s" % datetime.date.today().isoformat(),
        "- Command: `python3 tests/run.py cases --tier %s --jobs %d`" % (args.tier, args.jobs),
        "- claude CLI: %s" % (claude_version or "unknown"),
        "- Cases: %d. Wall clock: %d seconds with %d job(s)." % (len(chosen), wall, args.jobs),
        "- A case that fails once is rerun once; both attempts are listed.",
        "",
        "| Case | Tier | Result | Attempts | Seconds |",
        "| ---- | ---- | ------ | -------- | ------- |",
    ]
    for c in chosen:
        att = results[c["id"]]
        res = "PASS" if att[-1]["passed"] else "FAIL"
        if att[-1]["passed"] and len(att) > 1:
            res = "PASS (after rerun)"
        lines.append("| %s | %s | %s | %d | %d |" % (c["id"], c["tier"], res, len(att), sum(a["seconds"] for a in att)))
    problems = [(c["id"], a) for c in chosen for a in results[c["id"]] if not a["passed"]]
    if problems:
        lines += ["", "## Failed attempts", ""]
        for cid, a in problems:
            lines.append("- `%s`, attempt %d: %s" % (cid, a["attempt"], "; ".join(a["failures"])))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- main


def main(argv):
    ap = argparse.ArgumentParser(description="ai-toolkit test harness", formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = ap.add_subparsers(dest="layer", required=True)
    sub.add_parser("static", help="offline structure checks")
    sub.add_parser("scripts", help="check scripts against fixtures")
    c = sub.add_parser("cases", help="model-run cases through claude -p")
    c.add_argument("--list", action="store_true", help="list the cases and exit")
    c.add_argument("--tier", choices=TIERS, default="slow")
    c.add_argument("--case", action="append", help="run only this case id (repeatable)")
    c.add_argument("--jobs", type=int, default=2, help="parallel cases (default 2)")
    c.add_argument("--log", help="write the run log here (default tests/runs/model-cases-<version>.md)")
    c.add_argument("--no-log", action="store_true")
    c.add_argument("--no-retry", action="store_true", help="do not rerun a failed case")
    args = ap.parse_args(argv)
    return {"static": cmd_static, "scripts": cmd_scripts, "cases": cmd_cases}[args.layer](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
