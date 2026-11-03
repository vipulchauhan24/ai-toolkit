#!/usr/bin/env python3
"""Test runner for the ai-toolkit plugin. Python 3.9+, standard library only.

Usage (from the repository root):
  python3 -I tests/run.py static                 structure checks, offline, no model
  python3 -I tests/run.py scripts                check scripts against clean and seeded fixtures, offline
  python3 tests/run.py cases [options]           run skills and agents with the claude CLI, then assert
  python3 tests/run.py all [options]             static, scripts, then cases

Case options:
  --tier fast|slow|network   highest tier to run (default slow; network needs internet)
  --case ID                  run only this case (repeatable)
  --jobs N                   cases in parallel (default 2)
  --model NAME               pass --model to claude
  --log-dir DIR              transcripts and extracted output (default tests/runs/.cases)
  --list                     list cases and the files each one covers
  --dry-run                  show what would run

Every line is PASS, FAIL, XFAIL (known defect, expected to fail), XPASS (known defect fixed:
remove it from expected.json) or WARN. The last line is `RESULT  PASS` or `RESULT  FAIL`.
Exit code 1 on any FAIL or XPASS.
"""
import argparse
import ast
import concurrent.futures
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TESTS = REPO / "tests"
FIXTURES = TESTS / "fixtures"
CASES_DIR = TESTS / "cases"
TIERS = ["fast", "slow", "network"]

# Every script under skills/*/scripts must be named here, with the test that exercises it.
SCRIPT_COVERAGE = {
    "skills/frontend-react/scripts/check_react.py": "fixtures frontend-react/base and next",
    "skills/ui-developer/scripts/audit_ui.py": "fixtures ui-developer/base",
    "skills/design-system-builder/scripts/check_contrast.py": "fixtures design-system-builder",
    "skills/design-system-builder/scripts/check-contrast.sh": "usage test",
    "skills/design-system-builder/scripts/build_tokens_json.py": "fixtures design-system-builder",
}

counts = {"FAIL": 0, "XPASS": 0}


def rec(status, name, msg=""):
    if status in counts:
        counts[status] += 1
    print("%-5s %s%s" % (status, name, (": " + msg) if msg else ""), flush=True)


def check(ok, name, msg=""):
    rec("PASS" if ok else "FAIL", name, "" if ok else msg)
    return ok


def soft(ok, name, msg=""):
    rec("PASS" if ok else "WARN", name, "" if ok else msg)
    return ok


def rel(p):
    return str(Path(p).resolve().relative_to(REPO))


def frontmatter(path):
    lines = path.read_text(encoding="utf-8").split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return None
    fm, key = {}, None
    for line in lines[1:end]:
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if m and not line.startswith(" "):
            key, val = m.group(1), m.group(2).strip()
            fm[key] = "" if val in (">", "|", ">-", "|-") else val
        elif key and line.strip():
            fm[key] = (fm[key] + " " + line.strip()).strip()
    return fm


def rules_files():
    return sorted(p for p in (REPO / "rules").rglob("*.md") if p.name != "NOTICE.md")


def load_cases():
    cases = []
    for f in sorted(CASES_DIR.glob("*.json")):
        for c in json.loads(f.read_text(encoding="utf-8")):
            c["_file"] = f.name
            cases.append(c)
    return cases


# --------------------------------------------------------------------------- static


def static():
    print("== static ==")
    # manifests
    plugin = json.loads((REPO / ".claude-plugin/plugin.json").read_text())
    market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
    mv = market["plugins"][0].get("version")
    check(plugin.get("version") == mv, "manifest versions match", "plugin %r, marketplace %r" % (plugin.get("version"), mv))
    for s in plugin.get("skills", []):
        check((REPO / s).is_dir(), "plugin.json skills path exists: " + s)

    # skills
    for d in sorted(p for p in (REPO / "skills").iterdir() if p.is_dir()):
        n = "skill " + d.name
        md = d / "SKILL.md"
        if not check(md.is_file(), n + ": SKILL.md exists"):
            continue
        fm = frontmatter(md)
        if not check(fm is not None, n + ": front matter present"):
            continue
        check(fm.get("name") == d.name, n + ": name matches folder", "name is %r" % fm.get("name"))
        check(0 < len(fm.get("name", "")) <= 64, n + ": name length 1-64")
        desc = fm.get("description", "")
        check(0 < len(desc) <= 1024, n + ": description 1-1024 chars", "%d chars" % len(desc))
        if "model" in fm:
            check(fm["model"] in ("opus", "sonnet", "haiku", "inherit"), n + ": model value", fm["model"])
        lines = md.read_text(encoding="utf-8").count("\n") + 1
        check(lines < 500, n + ": SKILL.md under 500 lines", "%d lines" % lines)
        check((d / "README.md").is_file(), n + ": README.md exists")
        text = md.read_text(encoding="utf-8")
        for ref in sorted(set(re.findall(r"(?<![\w./-])((?:references|scripts)/[A-Za-z0-9_.-]+)", text))):
            check((d / ref).exists(), n + ": referenced file exists: " + ref)

    # agents
    for a in sorted((REPO / "agents").glob("*.md")):
        n = "agent " + a.stem
        fm = frontmatter(a)
        if not check(fm is not None, n + ": front matter present"):
            continue
        check(fm.get("name") == a.stem, n + ": name matches file", "name is %r" % fm.get("name"))
        check(bool(fm.get("description")), n + ": has description")
        check(bool(fm.get("tools")), n + ": has tools")

    # relative paths written in skills, agents, READMEs and rules resolve
    docs = (
        list((REPO / "skills").rglob("*.md"))
        + list((REPO / "agents").glob("*.md"))
        + list((REPO / "rules").rglob("*.md"))
        + [REPO / "templates/spec-template.md"]
    )
    path_re = re.compile(r"`((?:\.\./)+[A-Za-z0-9_./-]+|(?:rules|templates|references|scripts|agents|tests)/[A-Za-z0-9_./-]+\.[a-z]+)`")
    for doc in sorted(docs):
        for m in sorted(set(path_re.findall(doc.read_text(encoding="utf-8")))):
            if "*" in m or "<" in m:
                continue
            candidates = [doc.parent / m, REPO / m] + [Path(x) for x in glob.glob(str(REPO / "skills" / "*" / m))]
            if "skills" in doc.parts:
                candidates.append(REPO / "skills" / doc.relative_to(REPO / "skills").parts[0] / m)
            if len(doc.relative_to(REPO).parts) > 2 and doc.relative_to(REPO).parts[0] == "rules":
                candidates.append(REPO / "rules" / doc.relative_to(REPO / "rules").parts[0] / m)
            if not any(c.exists() for c in candidates):
                check(False, "path in %s resolves: %s" % (rel(doc), m), "not found")
    rec("PASS", "path references checked in %d documents" % len(docs))

    # scripts: syntax at Python 3.9, shell syntax
    for p in sorted((REPO / "skills").glob("*/scripts/*")):
        if not p.is_file():
            continue
        if p.suffix == ".py":
            try:
                ast.parse(p.read_text(encoding="utf-8"), filename=str(p), feature_version=(3, 9))
                ok, msg = True, ""
            except SyntaxError as e:
                ok, msg = False, str(e)
            check(ok, "script parses as Python 3.9: " + rel(p), msg)
        elif p.suffix == ".sh":
            r = subprocess.run(["bash", "-n", str(p)], capture_output=True, text=True)
            check(r.returncode == 0, "script parses as bash: " + rel(p), r.stderr.strip())
        check(rel(p) in SCRIPT_COVERAGE, "script has a test: " + rel(p), "add it to SCRIPT_COVERAGE in tests/run.py")

    # rules: size, contents list, not orphaned, not empty
    corpus = ""
    for p in list((REPO / "skills").rglob("*.md")) + list((REPO / "agents").glob("*.md")) + list((REPO / "rules").rglob("*.md")):
        corpus += p.read_text(encoding="utf-8") + "\n"
    for p in rules_files():
        n = "rule " + rel(p)
        t = p.read_text(encoding="utf-8")
        if not t.strip():
            rec("WARN", n, "empty file (planned content)")
            continue
        check(p.name in corpus.replace(p.read_text(encoding="utf-8"), ""), n + ": read by a skill, agent or other rule")
        lines = t.split("\n")
        hard = p.relative_to(REPO / "rules").parts[0] in ("coding", "database")
        verdict = check if hard else soft
        if len(lines) > 100:
            if not verdict("## Contents" in lines, n + ": has ## Contents (over 100 lines)"):
                continue
            heads = [re.sub(r"^\d+\.\s*", "", l[3:]).strip() for l in lines if l.startswith("## ") and l != "## Contents"]
            items = []
            for l in lines[lines.index("## Contents") + 1:]:
                if not l.strip():
                    if items:
                        break
                    continue
                m = re.match(r"\d+\.\s*(.*)", l)
                if not m:
                    break
                items.append(m.group(1).strip())
            verdict(items == heads, n + ": contents list matches headings", "contents %r vs headings %r" % (items, heads))

    # architecture-patterns: default table
    ap = (REPO / "rules/coding/architecture-patterns.md").read_text(encoding="utf-8")
    sec = ap.split("## 5. Default pattern per framework")[1].split("## 6.")[0]
    rows = [l for l in sec.split("\n") if l.startswith("| ") and not l.startswith("| Framework") and not l.startswith("| ---")]
    check(len(rows) == 7, "architecture-patterns default table has 7 rows", "%d rows" % len(rows))
    check(all(r.split("|")[2].strip() in ("mvc", "mvvm", "layered") for r in rows), "architecture-patterns defaults are mvc, mvvm or layered")

    # spec fixtures follow the spec template
    tpl = (REPO / "templates/spec-template.md").read_text(encoding="utf-8").split("## Project-type prompts")[0]
    heads = [l for l in tpl.split("\n") if l.startswith("## ") or l.startswith("### ")]
    for spec in sorted(FIXTURES.glob("project-planner-pattern/*-spec.md")):
        st = spec.read_text(encoding="utf-8")
        missing = [h for h in heads if h not in st]
        check(not missing, "spec fixture follows template: " + rel(spec), "missing %r" % missing)

    # cases: schema and coverage
    cases = load_cases()
    ids = [c["id"] for c in cases]
    check(len(ids) == len(set(ids)), "case ids are unique")
    covered = set()
    for c in cases:
        n = "case " + c["id"]
        for k in ("id", "tier", "covers", "prompt", "fixture"):
            if k not in c:
                check(False, n + ": has key " + k)
        if not all(k in c for k in ("id", "tier", "covers", "prompt", "fixture")):
            continue
        check(c["tier"] in TIERS, n + ": tier is valid", c["tier"])
        check((FIXTURES / c["fixture"]).is_dir(), n + ": fixture folder exists", c["fixture"])
        for cov in c["covers"]:
            check((REPO / cov).exists(), n + ": covers path exists: " + cov)
            covered.add(cov)
        patterns = list(c.get("must", [])) + list(c.get("must_not", []))
        for f in c.get("files", {}).values():
            patterns += f.get("must", []) + f.get("must_not", [])
        for pat in patterns:
            try:
                re.compile(pat)
            except re.error as e:
                check(False, n + ": regex compiles: " + pat, str(e))
    wanted = ["skills/" + p.name for p in (REPO / "skills").iterdir() if p.is_dir()]
    wanted += ["agents/" + p.name for p in (REPO / "agents").glob("*.md")]
    for p in rules_files():
        if p.read_text(encoding="utf-8").strip():
            wanted.append(rel(p))
    for w in sorted(wanted):
        check(w in covered, "covered by at least one model case: " + w, "add it to a case's covers list")


# --------------------------------------------------------------------------- scripts


def run_script(script, flags, files):
    return subprocess.run(
        [sys.executable, "-I", "-B", str(script)] + flags + [str(f) for f in files],
        capture_output=True, text=True, cwd=str(REPO),
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
    )


def scripts():
    print("== scripts ==")
    for set_dir in sorted(FIXTURES.glob("*/*/")):
        exp_file = set_dir / "expected.json"
        if not exp_file.is_file():
            continue
        skill, flagset = set_dir.parent.name, set_dir.name
        found = glob.glob(str(REPO / "skills" / skill / "scripts" / "check_*.py")) + glob.glob(str(REPO / "skills" / skill / "scripts" / "audit_*.py"))
        if not check(len(found) == 1, "%s/%s: exactly one check script" % (skill, flagset), "found %r" % found):
            continue
        script = found[0]
        flags = [] if flagset == "base" else ["--" + flagset]
        exp = json.loads(exp_file.read_text())
        clean = sorted(f for f in (set_dir / "clean").rglob("*") if f.is_file())
        check(len(clean) > 0, "%s/%s clean: has files" % (skill, flagset))
        r = run_script(script, flags, clean)
        check(r.returncode == 0 and "FAIL" not in r.stdout.replace("0 failure", ""),
              "%s/%s clean passes (%d files)" % (skill, flagset, len(clean)), (r.stdout + r.stderr).strip()[:300])
        entries = sorted((set_dir / "seeded").iterdir())
        for name in exp["seeded"]:
            check((set_dir / "seeded" / name).exists(), "%s/%s seeded %s exists" % (skill, flagset, name))
        for e in entries:
            name = e.name
            pattern = exp["seeded"].get(name)
            if not check(pattern is not None, "%s/%s seeded %s has an expected message" % (skill, flagset, name)):
                continue
            files = [e] if e.is_file() else sorted(f for f in e.rglob("*") if f.is_file())
            r = run_script(script, flags, files)
            fails = [l for l in r.stdout.split("\n") if l.startswith("FAIL")]
            ok = r.returncode == 1 and any(re.search(pattern, l) for l in fails)
            label = "%s/%s seeded %s fails with /%s/" % (skill, flagset, name, pattern)
            if name in exp.get("xfail", {}):
                rec("XPASS" if ok else "XFAIL", label, exp["xfail"][name] if not ok else "defect is fixed: remove it from expected.json")
            else:
                check(ok, label, "exit %d, FAIL lines %r" % (r.returncode, fails))
        # no arguments is a usage error, not a pass
        r = run_script(script, flags, [])
        check(r.returncode != 0, "%s/%s: no files is not a pass" % (skill, flagset), "exit %d" % r.returncode)

    # design-system-builder scripts
    dsb = REPO / "skills/design-system-builder/scripts"
    clean = FIXTURES / "design-system-builder/clean/Mini"
    seeded = FIXTURES / "design-system-builder/seeded/MiniLowContrast"
    r = run_script(dsb / "check_contrast.py", [], [clean])
    check(r.returncode == 0 and "0 problem(s)" in r.stdout, "design-system-builder: clean tokens pass contrast", r.stdout[-200:])
    r = run_script(dsb / "check_contrast.py", [], [seeded])
    check(r.returncode == 1 and re.search(r"FAIL\s+--color-text-primary on --color-surface", r.stdout) is not None,
          "design-system-builder: low contrast pair fails", r.stdout[-200:])
    r = run_script(dsb / "check_contrast.py", [], [FIXTURES])
    check(r.returncode != 0, "design-system-builder: folder without tokens.css is an error", "exit %d" % r.returncode)
    tmp = Path(tempfile.mkdtemp(prefix="dsb-"))
    try:
        shutil.copytree(clean, tmp / "Mini")
        r = run_script(dsb / "build_tokens_json.py", [], [tmp / "Mini"])
        ok = r.returncode == 0 and (tmp / "Mini/tokens.json").is_file()
        if ok:
            data = json.loads((tmp / "Mini/tokens.json").read_text())
            ok = "primitive" in data and "$value" in json.dumps(data)
        check(ok, "design-system-builder: tokens.json builds from tokens.css", (r.stdout + r.stderr).strip()[:200])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    r = subprocess.run(["bash", str(dsb / "check-contrast.sh")], capture_output=True, text=True)
    check(r.returncode == 2 and "usage" in r.stderr, "design-system-builder: check-contrast.sh without args prints usage and exits 2", "exit %d" % r.returncode)


# --------------------------------------------------------------------------- cases


def parse_stream(raw):
    """Return (final text, tool uses) from `claude -p --output-format stream-json --verbose`."""
    text, tools = "", []
    for line in raw.split("\n"):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "assistant":
            for b in ev.get("message", {}).get("content", []):
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    tools.append((b.get("name"), b.get("input", {})))
        elif ev.get("type") == "result":
            text = ev.get("result") or text
    return text, tools


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_case(c, args, log_dir):
    cid = c["id"]
    work_root = Path(tempfile.mkdtemp(prefix="case-%s-" % cid))
    work = work_root / "work"
    shutil.copytree(FIXTURES / c["fixture"], work)
    before = {p: sha(work / p) for p in c.get("unchanged", [])}
    tools = c.get("tools", "Read,Glob,Grep,Skill")
    cmd = ["claude", "-p", c["prompt"], "--plugin-dir", str(REPO), "--add-dir", str(REPO),
           "--permission-mode", "dontAsk", "--allowedTools", tools,
           "--output-format", "stream-json", "--verbose"]
    if args.model:
        cmd += ["--model", args.model]
    out = []
    try:
        r = subprocess.run(cmd, cwd=str(work), capture_output=True, text=True, timeout=c.get("timeout", 900))
        raw, err, rc = r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired as e:
        raw = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        err, rc = "timeout after %ss" % c.get("timeout", 900), 124
    text, used = parse_stream(raw)
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / (cid + ".stream.jsonl")).write_text(raw)
    (log_dir / (cid + ".txt")).write_text(text)

    def res(ok, what, msg=""):
        out.append(("PASS" if ok else "FAIL", "%s: %s" % (cid, what), "" if ok else msg))

    res(rc == 0 and bool(text), "claude ran and returned text", "exit %s %s" % (rc, err.strip()[:200]))
    for pat in c.get("must", []):
        res(re.search(pat, text, re.M) is not None, "output matches /%s/" % pat, "output starts: %r" % text[:200])
    for pat in c.get("must_not", []):
        res(re.search(pat, text, re.M) is None, "output does not match /%s/" % pat, "matched in output")
    skills = [i.get("skill", "") for n, i in used if n == "Skill"]
    for s in c.get("skills", []):
        res(any(x == s or x.endswith(":" + s) or x.endswith(s) for x in skills), "invoked skill " + s, "Skill calls: %r" % skills)
    agents = [i.get("subagent_type", "") for n, i in used if n in ("Agent", "Task")]
    for a in c.get("agents", []):
        res(any(x.endswith(a) for x in agents), "invoked agent " + a, "Agent calls: %r" % agents)
    reads = [i.get("file_path", "") for n, i in used if n == "Read"]
    for pat in c.get("reads", []):
        res(any(re.search(pat, p) for p in reads), "read a file matching /%s/" % pat, "Read calls: %r" % reads)
    for pat, spec in c.get("files", {}).items():
        matches = sorted(work.glob(pat))
        want = spec.get("exists", True)
        if not want:
            res(not matches, "file absent: " + pat, "found %r" % [str(m.relative_to(work)) for m in matches])
            continue
        if not matches:
            res(False, "file exists: " + pat, "no match")
            continue
        res(True, "file exists: " + pat)
        for m in matches:
            body = m.read_text(encoding="utf-8", errors="replace") if m.is_file() else ""
            for p in spec.get("must", []):
                res(re.search(p, body, re.M) is not None, "%s matches /%s/" % (m.name, p), "no match")
            for p in spec.get("must_not", []):
                res(re.search(p, body, re.M) is None, "%s does not match /%s/" % (m.name, p), "matched")
    for pat in c.get("no_files", []):
        found = [str(m.relative_to(work)) for m in work.glob(pat)]
        res(not found, "no files match " + pat, "found %r" % found)
    for p, h in before.items():
        res((work / p).exists() and sha(work / p) == h, "unchanged: " + p, "file changed or removed")
    for cmdline in c.get("post", []):
        pr = subprocess.run(cmdline.replace("{repo}", str(REPO)), shell=True, cwd=str(work), capture_output=True, text=True)
        res(pr.returncode == 0, "post command succeeds: " + cmdline[:80], (pr.stdout + pr.stderr).strip()[-300:])
    shutil.rmtree(work_root, ignore_errors=True)
    return out


def cases(args):
    print("== cases ==")
    allc = load_cases()
    top = TIERS.index(args.tier)
    selected = [c for c in allc if TIERS.index(c["tier"]) <= top and (not args.case or c["id"] in args.case)]
    if args.case:
        unknown = [i for i in args.case if i not in [c["id"] for c in allc]]
        if unknown:
            rec("FAIL", "unknown case ids", repr(unknown))
            return
    if args.list or args.dry_run:
        for c in selected:
            print("%-8s %-34s covers: %s" % (c["tier"], c["id"], ", ".join(c["covers"])))
        return
    if shutil.which("claude") is None:
        rec("FAIL", "claude CLI is on PATH", "install Claude Code, or run `static` and `scripts` only")
        return
    log_dir = Path(args.log_dir) if args.log_dir else TESTS / "runs" / ".cases"
    print("logs: %s" % log_dir, flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = {ex.submit(run_case, c, args, log_dir): c for c in selected}
        for f in concurrent.futures.as_completed(futs):
            for status, name, msg in f.result():
                rec(status, name, msg)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("layer", choices=["static", "scripts", "cases", "all"])
    ap.add_argument("--tier", default="slow", choices=TIERS)
    ap.add_argument("--case", action="append")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--model")
    ap.add_argument("--log-dir")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.layer in ("static", "all"):
        static()
    if args.layer in ("scripts", "all"):
        scripts()
    if args.layer in ("cases", "all"):
        cases(args)
    failed = counts["FAIL"] + counts["XPASS"]
    print("RESULT  " + ("FAIL" if failed else "PASS"))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
