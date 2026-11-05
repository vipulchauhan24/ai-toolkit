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
  scripts  Check scripts run against clean and seeded fixtures, and the
           design-system-builder scripts. Offline, no model.
  cases    Skills and agents run through `claude -p` with the plugin loaded from
           this checkout, then asserted. Needs the `claude` CLI and uses tokens.

Output lines start with PASS, FAIL, WARN, XFAIL, XPASS, RETRY or RESULT. A run
passes when it prints `RESULT  PASS`. FAIL and XPASS lines fail the run; WARN and
XFAIL lines are listed in the release notes and do not.

Tiers: fast (under about a minute each), slow (several minutes), network (needs
internet, for Ember). `--tier fast` runs fast; `--tier slow` runs fast and slow
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
    "skills/ui-developer/scripts/audit_ui.py": "tests/fixtures/ui-developer",
    "skills/design-system-builder/scripts/check_contrast.py": "tests/fixtures/design-system-builder",
    "skills/design-system-builder/scripts/check_contrast.sh": "tests/fixtures/design-system-builder",
    "skills/design-system-builder/scripts/build_tokens_json.py": "tests/fixtures/design-system-builder",
}
REQUIRED_FIXTURES = [
    "doc-trimmer",
    "doc-reviewer",
    "project-planner-pattern",
    "project-planner-pattern/sample-project",
    "project-planner-pattern/conflicting-spec.md",
    "project-planner-greenfield",
    "frontend-react-projects",
    "ui-developer-projects",
    "skill-runner",
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
    audit = ROOT / "skills" / "ui-developer" / "scripts" / "audit_ui.py"
    for label, script, args in (
        ("check_react.py with no file", react, []),
        ("check_react.py with only --next", react, ["--next"]),
        ("audit_ui.py with no file", audit, []),
    ):
        rc, out = run_py(script, args)
        r.check("usage error: %s exits 2" % label, rc == 2, "exit %d" % rc)

    # design-system-builder scripts
    dsb = ROOT / "skills" / "design-system-builder" / "scripts"
    mini = FIXTURES / "design-system-builder" / "clean" / "Mini"
    low = FIXTURES / "design-system-builder" / "seeded" / "MiniLowContrast"
    rc, out = run_py(dsb / "check_contrast.py", [rel(mini)])
    r.check("check_contrast.py: clean Mini passes", rc == 0, "exit %d: %s" % (rc, out.strip()[-200:]))
    rc, out = run_py(dsb / "check_contrast.py", [rel(low)])
    hit = re.search(r"^\s*FAIL\s+--color-text-muted on --color-surface", out, re.M)
    r.check("check_contrast.py: MiniLowContrast fails on text-muted", rc == 1 and bool(hit), "exit %d: %s" % (rc, out.strip()[-200:]))
    tmp = Path(tempfile.mkdtemp(prefix="tokens-"))
    try:
        work = tmp / "Mini"
        shutil.copytree(mini, work)
        rc, out = run_py(dsb / "build_tokens_json.py", [work])
        ok = rc == 0 and (work / "tokens.json").is_file()
        detail = "exit %d: %s" % (rc, out.strip()[-200:])
        if ok:
            try:
                data = json.loads(read(work / "tokens.json"))
                blue = data["primitive"]["blue"]["600"]
                ok = str(blue.get("$value", "")).lower() == "#2563eb" and "$extensions" in read(work / "tokens.json")
                detail = "tokens.json content differs from the Mini fixture: %s" % blue
            except (ValueError, KeyError, TypeError) as e:
                ok, detail = False, "tokens.json: %r" % (e,)
        r.check("build_tokens_json.py: writes tokens.json with primitives and dark overrides", ok, detail)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    p = subprocess.run(["bash", str(dsb / "check_contrast.sh")], capture_output=True, text=True)
    r.check("usage error: check_contrast.sh with no argument exits 2", p.returncode == 2, "exit %d" % p.returncode)
    rc, out = run_py(dsb / "build_tokens_json.py", [])
    r.check("usage error: build_tokens_json.py with no argument prints usage", rc != 0 and "usage" in out, "exit %d" % rc)

    return r.finish()


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
