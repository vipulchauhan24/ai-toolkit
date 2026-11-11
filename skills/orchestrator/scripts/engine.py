#!/usr/bin/env python3
"""Route engine for the orchestrator skill. Standard library only, Python 3.9 or later.

The engine keeps the project's route (a DAG of phases) and its ledger (what each phase
is doing), and says what may start next. It starts nothing: the orchestrator launches
the helpers and tells the engine what happened.

Usage (from the project root):

    python3 -I engine.py validate                     check route.json
    python3 -I engine.py init                         create state.json from route.json
    python3 -I engine.py approve gate-a [--file F]    record the approved spec
    python3 -I engine.py approve gate-b               record the approved route
    python3 -I engine.py next                         JSON: what may start now
    python3 -I engine.py start ID [ID ...]            mark phases running, JSON: runner calls
    python3 -I engine.py record ID RUN_DIR [--tokens N]
                                                      read RUN_DIR/report.md, mark built or failed
    python3 -I engine.py pushed ID BRANCH             record the pushed branch of a built phase
    python3 -I engine.py merge ID                     mark a built phase (or a finished parked step) merged
    python3 -I engine.py fail ID --reason TEXT        mark a running or built phase failed
    python3 -I engine.py retry ID                     send a failed, running or built phase back to pending
    python3 -I engine.py status                       table of phases and gates

Options for every command: --root DIR (default: current directory) and --dir DIR
(default: ROOT/.orchestrator, holds route.json and state.json).

Output: validate, init, approve, record, pushed, merge, fail and retry print FAIL lines and
end with `RESULT  PASS` or `RESULT  FAIL`. next and start print one JSON object.
Exit codes: 0 done, 1 refused or failed, 2 usage error.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
from pathlib import Path

ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
SKILL_RE = re.compile(r"^[a-z0-9][a-z0-9-]*(:[a-z0-9][a-z0-9-]*)?$")
MODEL_RE = re.compile(r"^[a-z0-9][a-z0-9.-]*$")
ISOLATION = ("required", "not required")
STATUSES = ("pending", "running", "built", "merged", "failed")
RUNNER = "ai-toolkit:skill-runner"
STATUS_RE = re.compile(
    r"^[\s>*_`#-]*status[\s*_`]*[:=]?[\s*_`]*(done with assumptions|done|failed|blocked|running|partial)\b",
    re.I | re.M,
)
EVIDENCE_RE = re.compile(r"\bevidence\b", re.I)


class Refusal(Exception):
    """The command is refused. `lines` are printed as FAIL lines."""

    def __init__(self, *lines):
        super().__init__("; ".join(lines))
        self.lines = list(lines)


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def overlap(a_files, b_files):
    """First file that two phases both change, or None. A path ending in / stands for everything under it."""
    for x in a_files:
        for y in b_files:
            if x == y or (x.endswith("/") and y.startswith(x)) or (y.endswith("/") and x.startswith(y)):
                return x if len(x) >= len(y) else y
    return None


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as e:
        raise Refusal("%s cannot be read: %s" % (path, e.strerror or e))
    except ValueError as e:
        raise Refusal("%s is not valid JSON: %s" % (path, e))


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    os.replace(str(tmp), str(path))


# ---------------------------------------------------------------- route


def ancestors(phases):
    """Map id -> set of every phase it depends on, directly or not. Assumes no cycle."""
    deps = {p["id"]: list(p.get("depends_on", [])) for p in phases}
    memo = {}

    def walk(i, seen):
        if i in memo:
            return memo[i]
        out = set()
        for d in deps.get(i, []):
            if d in deps and d not in seen:
                out.add(d)
                out |= walk(d, seen | {i})
        memo[i] = out
        return out

    return {i: walk(i, frozenset()) for i in deps}


def validate_route(route, root, check_docs=True):
    """Return (fails, warns, info). A route with any fail line must not be approved."""
    fails, warns = [], []
    if not isinstance(route, dict):
        return ["route.json must hold a JSON object"], warns, ""
    if route.get("version") != 1:
        fails.append("version must be 1")
    if not isinstance(route.get("project"), str) or not route.get("project", "").strip():
        fails.append("project must be a non-empty string")
    if not isinstance(route.get("spec"), str) or not route.get("spec", "").strip():
        fails.append("spec must be the path of the approved spec")
    mp = route.get("max_parallel", 3)
    if not isinstance(mp, int) or isinstance(mp, bool) or mp < 1:
        fails.append("max_parallel must be a whole number of 1 or more")
    phases = route.get("phases")
    if not isinstance(phases, list) or not phases:
        fails.append("phases must be a non-empty list")
        return fails, warns, ""

    ids = []
    for n, p in enumerate(phases):
        if not isinstance(p, dict):
            fails.append("phase %d is not an object" % (n + 1))
            continue
        pid = p.get("id")
        if not isinstance(pid, str) or not ID_RE.match(pid):
            fails.append("phase %d: id must be lowercase letters, digits, - or _ (got %r)" % (n + 1, pid))
            continue
        if pid in ids:
            fails.append("duplicate phase id %s" % pid)
        ids.append(pid)
    if fails:
        return fails, warns, ""

    idset = set(ids)
    for p in phases:
        pid = p["id"]
        if not isinstance(p.get("title"), str) or not p["title"].strip():
            fails.append("%s: title must be a non-empty string" % pid)
        doc = p.get("doc")
        if not isinstance(doc, str) or not doc.strip():
            fails.append("%s: doc must be the path of the phase document" % pid)
        elif check_docs and not (Path(root) / doc).is_file():
            fails.append("%s: phase document %s does not exist" % (pid, doc))
        dep = p.get("depends_on", [])
        if not isinstance(dep, list) or not all(isinstance(d, str) for d in dep):
            fails.append("%s: depends_on must be a list of phase ids" % pid)
            dep = []
        for d in dep:
            if d == pid:
                fails.append("%s: depends on itself" % pid)
            elif d not in idset:
                fails.append("%s: depends on %s, which is not a phase" % (pid, d))
        parked = p.get("parked", False)
        if not isinstance(parked, bool):
            fails.append("%s: parked must be true or false" % pid)
            parked = False
        if parked:
            if not isinstance(p.get("park_reason"), str) or not p["park_reason"].strip():
                fails.append("%s: a parked phase needs a park_reason" % pid)
            ms = p.get("main_session_skill")
            if ms is not None and (not isinstance(ms, str) or not SKILL_RE.match(ms)):
                fails.append("%s: main_session_skill must be a skill name such as ai-toolkit:design-md" % pid)
        else:
            if p.get("main_session_skill") is not None:
                fails.append("%s: main_session_skill only belongs on a parked phase" % pid)
            skills = p.get("skills")
            if not isinstance(skills, list) or not skills:
                fails.append("%s: skills must be a non-empty list (or set parked)" % pid)
            else:
                for s in skills:
                    if not isinstance(s, str) or not SKILL_RE.match(s):
                        fails.append("%s: %r is not a skill name such as ai-toolkit:backend-node" % (pid, s))
            if not isinstance(p.get("model"), str) or not MODEL_RE.match(p.get("model", "")):
                fails.append("%s: model must be a model name such as sonnet" % pid)
            if p.get("isolation") not in ISOLATION:
                fails.append("%s: isolation must be 'required' or 'not required'" % pid)
        files = p.get("files", [])
        if not isinstance(files, list) or not all(isinstance(f, str) and f.strip() for f in files):
            fails.append("%s: files must be a list of paths" % pid)
        elif any(re.search(r"[*?{}\[\]]", f) for f in files):
            fails.append("%s: files must be paths or directories ending in /, not patterns (got %s)" % (pid, next(f for f in files if re.search(r"[*?{}\[\]]", f))))
        elif not parked and p.get("isolation") == "required" and not files:
            warns.append("%s: no files listed, so file clashes cannot be checked" % pid)
    if fails:
        return fails, warns, ""

    # Cycles: whatever Kahn's algorithm cannot remove sits on or behind a cycle.
    indeg = {p["id"]: len(p.get("depends_on", [])) for p in phases}
    kids = {i: [] for i in ids}
    for p in phases:
        for d in p.get("depends_on", []):
            kids[d].append(p["id"])
    queue = [i for i in ids if indeg[i] == 0]
    seen = 0
    while queue:
        i = queue.pop()
        seen += 1
        for k in kids[i]:
            indeg[k] -= 1
            if indeg[k] == 0:
                queue.append(k)
    if seen != len(ids):
        left = sorted(i for i in ids if indeg[i] > 0)
        fails.append("dependency cycle among: %s" % ", ".join(left))
        return fails, warns, ""

    # Two phases that can run together must not change the same file.
    anc = ancestors(phases)
    byid = {p["id"]: p for p in phases}
    for n, a in enumerate(ids):
        for b in ids[n + 1:]:
            if a in anc[b] or b in anc[a]:
                continue
            both = overlap(byid[a].get("files", []), byid[b].get("files", []))
            if both:
                fails.append("%s and %s can run together but both change %s: add a dependency between them or remove the file from one" % (a, b, both))

    edges = sum(len(p.get("depends_on", [])) for p in phases)
    info = "%d phases, %d dependencies, longest chain %d" % (len(ids), edges, longest_chain(phases))
    return fails, warns, info


def longest_chain(phases):
    deps = {p["id"]: list(p.get("depends_on", [])) for p in phases}
    memo = {}

    def depth(i):
        if i not in memo:
            memo[i] = 1 + max([depth(d) for d in deps[i]], default=0)
        return memo[i]

    return max(depth(i) for i in deps)


# ---------------------------------------------------------------- state


class Project:
    def __init__(self, root, dir_):
        self.root = Path(root).resolve()
        self.dir = Path(dir_).resolve() if dir_ else self.root / ".orchestrator"
        self.route_path = self.dir / "route.json"
        self.state_path = self.dir / "state.json"

    def route(self):
        return read_json(self.route_path)

    def state(self):
        if not self.state_path.is_file():
            raise Refusal("%s does not exist: run `init` first" % self.state_path)
        return read_json(self.state_path)

    def save(self, state):
        write_json(self.state_path, state)

    def abs(self, rel_path):
        p = Path(rel_path)
        return str(p if p.is_absolute() else self.root / p)


def log(state, cmd, phase="", detail=""):
    state.setdefault("events", []).append({"at": now(), "cmd": cmd, "phase": phase, "detail": detail})


def new_phase_state():
    return {"status": "pending", "attempts": 0, "run_dir": None, "started": None, "ended": None, "note": "", "tokens": None}


def phase_map(route):
    return {p["id"]: p for p in route["phases"]}


def gate_problems(proj, route, state):
    """Reasons `next` and `start` must refuse. Empty means both gates hold."""
    out = []
    gates = state.get("gates", {})
    a, b = gates.get("a"), gates.get("b")
    if not a:
        out.append("Gate A is not approved: run `approve gate-a` after you approve the spec")
    else:
        spec = Path(proj.abs(route["spec"]))
        if not spec.is_file():
            out.append("the approved spec %s is missing" % route["spec"])
        elif sha256_file(spec) != a["hash"]:
            out.append("the spec changed since Gate A: approve it again")
    if not b:
        out.append("Gate B is not approved: run `approve gate-b` after you confirm the route")
    elif not proj.route_path.is_file() or sha256_file(proj.route_path) != b["hash"]:
        out.append("the route changed since Gate B: validate it and approve Gate B again")
    return out


def plan(route, state, proj):
    """Work out what may start. Returns a dict of lists plus `done`."""
    phases = route["phases"]
    byid = phase_map(route)
    st = state["phases"]
    anc = ancestors(phases)
    failed = [i for i in byid if st[i]["status"] == "failed"]
    in_progress = [i for i in byid if st[i]["status"] in ("running", "built")]
    running = [i for i in byid if st[i]["status"] == "running"]
    cap = route.get("max_parallel", 3) - len(running)

    ready, parked, held, halted = [], [], [], []
    taken = []  # files of phases that are running, built or about to start
    for i in in_progress:
        taken.append((i, byid[i].get("files", [])))
    for p in phases:
        i = p["id"]
        if st[i]["status"] != "pending":
            continue
        bad = sorted(d for d in anc[i] if d in failed)
        if bad:
            halted.append({"id": i, "why": "depends on failed %s" % ", ".join(bad)})
            continue
        waiting = [d for d in p.get("depends_on", []) if st[d]["status"] != "merged"]
        if waiting:
            held.append({"id": i, "why": "waiting for %s" % ", ".join(waiting)})
            continue
        if p.get("parked"):
            parked.append({"id": i, "title": p["title"], "reason": p["park_reason"],
                           "main_session_skill": p.get("main_session_skill")})
            continue
        mine = p.get("files", [])
        clash = next(((j, hit) for j, f in taken for hit in [overlap(mine, f)] if hit), None)
        if clash:
            held.append({"id": i, "why": "shares %s with %s, which is not merged yet" % (clash[1], clash[0])})
            continue
        if cap <= 0:
            held.append({"id": i, "why": "worker cap of %d reached" % route.get("max_parallel", 3)})
            continue
        cap -= 1
        taken.append((i, mine))
        ready.append({"id": i, "title": p["title"], "skills": p["skills"], "model": p["model"], "isolation": p["isolation"]})
    done = all(st[i]["status"] == "merged" for i in byid)
    stuck = (not done) and not ready and not parked and not in_progress
    return {"ready": ready, "parked": parked, "held": held, "halted": halted,
            "in_progress": [{"id": i, "status": st[i]["status"]} for i in in_progress],
            "failed": [{"id": i, "note": st[i]["note"]} for i in failed],
            "done": done, "stuck": stuck}


# ---------------------------------------------------------------- report


def check_report(text, skills):
    """Return the reasons a runner report does not prove the phase was built."""
    problems = []
    found = [m.group(1).lower() for m in STATUS_RE.finditer(text)]
    if not found:
        return ["the report has no status line"]
    bad = sorted({s for s in found if s not in ("done", "done with assumptions")})
    if bad:
        problems.append("the report says %s" % ", ".join(bad))
    if len(found) < len(skills):
        problems.append("the report has %d status line(s) for %d skill(s)" % (len(found), len(skills)))
    ev = len(EVIDENCE_RE.findall(text))
    if ev < len(skills):
        problems.append("the report has %d evidence line(s) for %d skill(s)" % (ev, len(skills)))
    for s in skills:
        short = s.split(":")[-1]
        if short not in text:
            problems.append("the report never mentions %s" % short)
    return problems


# ---------------------------------------------------------------- commands


def out_result(fails):
    for f in fails:
        print("FAIL  " + f)
    print("RESULT  " + ("FAIL" if fails else "PASS"))
    return 1 if fails else 0


def cmd_validate(proj, args):
    route = proj.route()
    fails, warns, info = validate_route(route, proj.root, check_docs=not args.no_docs)
    for w in warns:
        print("WARN  " + w)
    if not fails:
        print("OK  " + info)
    return out_result(fails)


def cmd_init(proj, args):
    route = proj.route()
    fails, _, _ = validate_route(route, proj.root)
    if fails:
        return out_result(fails)
    if proj.state_path.exists():
        return out_result(["%s already exists: init runs once per project" % proj.state_path])
    state = {"version": 1, "project": route["project"], "gates": {},
             "phases": {p["id"]: new_phase_state() for p in route["phases"]}, "events": []}
    log(state, "init")
    proj.save(state)
    print("OK  state created for %d phases" % len(route["phases"]))
    return out_result([])


def cmd_approve(proj, args):
    route = proj.route()
    state = proj.state()
    if args.gate == "gate-a":
        spec = Path(proj.abs(args.file or route["spec"]))
        if not spec.is_file():
            return out_result(["the spec %s does not exist" % spec])
        state["gates"] = {"a": {"hash": sha256_file(spec), "at": now(), "file": args.file or route["spec"]}}
        log(state, "approve gate-a")
        proj.save(state)
        print("OK  Gate A recorded; Gate B must be approved again")
        return out_result([])
    # gate-b
    a = state.get("gates", {}).get("a")
    spec = Path(proj.abs(route["spec"]))
    if not a or not spec.is_file() or sha256_file(spec) != a["hash"]:
        return out_result(["approve Gate A first, and the spec must not have changed since"])
    fails, _, _ = validate_route(route, proj.root)
    if fails:
        return out_result(fails)
    ids = set(phase_map(route))
    gone = sorted(i for i in state["phases"] if i not in ids)
    kept = [i for i in gone if state["phases"][i]["status"] != "pending"]
    if kept:
        return out_result(["the route drops %s, which already started: keep it in the route" % ", ".join(kept)])
    for i in gone:
        del state["phases"][i]
    added = [i for i in ids if i not in state["phases"]]
    for i in added:
        state["phases"][i] = new_phase_state()
    state["gates"]["b"] = {"hash": sha256_file(proj.route_path), "at": now()}
    log(state, "approve gate-b", detail="added %s, dropped %s" % (sorted(added), gone))
    proj.save(state)
    print("OK  Gate B recorded; %d phase(s) added, %d dropped" % (len(added), len(gone)))
    return out_result([])


def load_all(proj):
    route = proj.route()
    state = proj.state()
    fails, _, _ = validate_route(route, proj.root)
    if fails:
        raise Refusal(*fails)
    if set(state["phases"]) != set(phase_map(route)):
        raise Refusal("the route and the ledger list different phases: approve Gate B again")
    return route, state


def cmd_next(proj, args):
    route, state = load_all(proj)
    problems = gate_problems(proj, route, state)
    if problems:
        return out_result(problems)
    print(json.dumps(plan(route, state, proj), indent=2))
    return 0


def cmd_start(proj, args):
    route, state = load_all(proj)
    problems = gate_problems(proj, route, state)
    if problems:
        return out_result(problems)
    byid = phase_map(route)
    started = []
    for pid in args.ids:
        if pid not in byid:
            return out_result(["%s is not a phase" % pid])
        now_plan = plan(route, state, proj)
        if pid not in {r["id"] for r in now_plan["ready"]}:
            why = next((h["why"] for h in now_plan["held"] + now_plan["halted"] if h["id"] == pid),
                       "it is %s" % state["phases"][pid]["status"])
            if byid[pid].get("parked") and state["phases"][pid]["status"] == "pending" and pid in {x["id"] for x in now_plan["parked"]}:
                why = "it is parked for you, not for a helper"
            return out_result(["%s may not start: %s" % (pid, why)])
        ps = state["phases"][pid]
        ps["attempts"] += 1
        run_dir = proj.dir / "runs" / ("%s-%d" % (pid, ps["attempts"]))
        run_dir.parent.mkdir(parents=True, exist_ok=True)
        ps.update({"status": "running", "run_dir": str(run_dir), "started": now(), "ended": None, "note": ""})
        log(state, "start", pid, str(run_dir))
        p = byid[pid]
        started.append({
            "id": pid, "attempt": ps["attempts"], "agent": RUNNER, "skills": p["skills"], "model": p["model"],
            "isolation": p["isolation"], "run_dir": str(run_dir),
            "inputs": [proj.abs(p["doc"]), proj.abs(route["spec"])],
        })
    proj.save(state)
    print(json.dumps({"started": started}, indent=2))
    return 0


def cmd_record(proj, args):
    route, state = load_all(proj)
    byid = phase_map(route)
    if args.id not in byid:
        return out_result(["%s is not a phase" % args.id])
    ps = state["phases"][args.id]
    if ps["status"] != "running":
        return out_result(["%s is %s, not running" % (args.id, ps["status"])])
    report = Path(args.run_dir) / "report.md"
    if not report.is_file():
        problems = ["%s does not exist: the runner died or wrote elsewhere" % report]
    else:
        problems = check_report(report.read_text(encoding="utf-8", errors="replace"), byid[args.id]["skills"])
    ps["ended"] = now()
    ps["run_dir"] = str(Path(args.run_dir).resolve())
    if args.tokens is not None:
        ps["tokens"] = args.tokens
    if problems:
        ps["status"], ps["note"] = "failed", "; ".join(problems)
        log(state, "record", args.id, "failed: " + ps["note"])
        proj.save(state)
        return out_result(["%s failed: %s" % (args.id, x) for x in problems])
    ps["status"], ps["note"] = "built", ""
    log(state, "record", args.id, "built")
    proj.save(state)
    print("OK  %s built; it stays locked for its dependents until `merge %s`" % (args.id, args.id))
    return out_result([])


def cmd_merge(proj, args):
    route, state = load_all(proj)
    byid = phase_map(route)
    if args.id not in byid:
        return out_result(["%s is not a phase" % args.id])
    ps = state["phases"][args.id]
    parked_ready = (byid[args.id].get("parked") and ps["status"] == "pending"
                    and all(state["phases"][d]["status"] == "merged" for d in byid[args.id].get("depends_on", [])))
    if ps["status"] != "built" and not parked_ready:
        return out_result(["%s is %s: only a built phase, or a parked phase whose dependencies are merged, can be marked merged" % (args.id, ps["status"])])
    ps.update({"status": "merged", "ended": now()})
    log(state, "merge", args.id)
    proj.save(state)
    print("OK  %s merged" % args.id)
    return out_result([])


def cmd_pushed(proj, args):
    route, state = load_all(proj)
    if args.id not in state["phases"]:
        return out_result(["%s is not a phase" % args.id])
    ps = state["phases"][args.id]
    if ps["status"] != "built":
        return out_result(["%s is %s: only a built phase has a branch to push" % (args.id, ps["status"])])
    if not args.branch.strip():
        return out_result(["the branch name is empty"])
    ps["branch"] = args.branch
    log(state, "pushed", args.id, args.branch)
    proj.save(state)
    print("OK  %s pushed on %s; it stays locked for its dependents until `merge %s`" % (args.id, args.branch, args.id))
    return out_result([])


def cmd_fail(proj, args):
    route, state = load_all(proj)
    if args.id not in state["phases"]:
        return out_result(["%s is not a phase" % args.id])
    ps = state["phases"][args.id]
    if ps["status"] not in ("running", "built"):
        return out_result(["%s is %s: only a running or built phase can be failed" % (args.id, ps["status"])])
    ps.update({"status": "failed", "note": args.reason, "ended": now()})
    log(state, "fail", args.id, args.reason)
    proj.save(state)
    print("OK  %s failed; phases that depend on it are halted" % args.id)
    return out_result([])


def cmd_retry(proj, args):
    route, state = load_all(proj)
    if args.id not in state["phases"]:
        return out_result(["%s is not a phase" % args.id])
    ps = state["phases"][args.id]
    if ps["status"] not in ("failed", "running", "built"):
        return out_result(["%s is %s: nothing to retry" % (args.id, ps["status"])])
    ps.update({"status": "pending", "note": "", "ended": None})
    log(state, "retry", args.id)
    proj.save(state)
    print("OK  %s is pending again; the next run gets a new run directory" % args.id)
    return out_result([])


def cmd_status(proj, args):
    route, state = load_all(proj)
    p = plan(route, state, proj)
    halted = {h["id"] for h in p["halted"]}
    print("%-14s %-9s %-24s %s" % ("phase", "status", "depends on", "note"))
    for ph in route["phases"]:
        i = ph["id"]
        s = state["phases"][i]
        label = "halted" if i in halted else s["status"]
        print("%-14s %-9s %-24s %s" % (i, label, ",".join(ph.get("depends_on", [])) or "-", s["note"] or (("pushed: " + s["branch"]) if s.get("branch") else "")))
    gates = state.get("gates", {})
    print("Gate A: %s   Gate B: %s" % ("approved" if "a" in gates else "not approved", "approved" if "b" in gates else "not approved"))
    merged = sum(1 for i in state["phases"] if state["phases"][i]["status"] == "merged")
    print("%d of %d merged" % (merged, len(state["phases"])))
    return 0


COMMANDS = {
    "validate": cmd_validate, "init": cmd_init, "approve": cmd_approve, "next": cmd_next,
    "start": cmd_start, "record": cmd_record, "pushed": cmd_pushed, "merge": cmd_merge, "fail": cmd_fail,
    "retry": cmd_retry, "status": cmd_status,
}


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", default=".", help="project root (default: current directory)")
    common.add_argument("--dir", default=None, help="folder with route.json and state.json (default: ROOT/.orchestrator)")
    ap = argparse.ArgumentParser(prog="engine.py", description="Route engine for the orchestrator skill.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate", parents=[common])
    v.add_argument("--no-docs", action="store_true", help="do not check that phase documents exist")
    sub.add_parser("init", parents=[common])
    a = sub.add_parser("approve", parents=[common])
    a.add_argument("gate", choices=["gate-a", "gate-b"])
    a.add_argument("--file", default=None, help="gate-a only: the spec to hash (default: the route's spec)")
    sub.add_parser("next", parents=[common])
    s = sub.add_parser("start", parents=[common])
    s.add_argument("ids", nargs="+")
    r = sub.add_parser("record", parents=[common])
    r.add_argument("id")
    r.add_argument("run_dir")
    r.add_argument("--tokens", type=int, default=None, help="total tokens the run used, if known")
    pu = sub.add_parser("pushed", parents=[common])
    pu.add_argument("id")
    pu.add_argument("branch")
    for name in ("merge", "retry"):
        m = sub.add_parser(name, parents=[common])
        m.add_argument("id")
    f = sub.add_parser("fail", parents=[common])
    f.add_argument("id")
    f.add_argument("--reason", required=True)
    sub.add_parser("status", parents=[common])
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    proj = Project(args.root, args.dir)
    try:
        return COMMANDS[args.cmd](proj, args)
    except Refusal as e:
        return out_result(e.lines)


if __name__ == "__main__":
    sys.exit(main())
