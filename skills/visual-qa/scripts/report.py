#!/usr/bin/env python3
"""Checks the grades for a capture and builds the report. Standard library only.

Usage:

    python3 -I report.py --run DIR --skeleton    write DIR/grades.json for the grader to fill in
    python3 -I report.py --run DIR               validate grades.json, write report.html and summary.md

The grader gives seven areas a letter and a reason. This script applies the caps from
the measured checks, works out motion and the overall grades, and writes the report.
A low grade is not a failure: FAIL means the grades or the capture are incomplete.

Output lines start with OK, FAIL or RESULT. Exit codes: 0 done, 1 failed, 2 usage error.
"""
from __future__ import annotations

import argparse
import base64
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "report-template.html"

GRADED = ("layout", "spacing", "typography", "color", "imagery", "responsive", "accessibility")
AREA_NAMES = {
    "layout": "Layout and alignment", "spacing": "Spacing", "typography": "Typography", "color": "Colour and contrast",
    "imagery": "Imagery and icons", "responsive": "Responsiveness", "motion": "Motion", "accessibility": "Accessibility",
}
POINTS = {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
LETTERS = "FDCBA"

# check id -> (area, best grade when it fails, best grade when it warns). See references/checks.md.
CAPS = {
    "overflow": ("responsive", "D", "D"), "margins": ("layout", "C", "C"), "empty-band": ("spacing", "C", "B"),
    "hidden-content": ("motion", "D", "D"), "tap-target": ("responsive", "C", None), "broken-image": ("imagery", "D", "D"),
    "img-alt": ("accessibility", "C", "C"), "h1": ("accessibility", "C", "C"), "small-text": ("typography", "C", "B"),
    "long-lines": ("typography", "C", "B"), "contrast": ("color", "C", "C"), "field-label": ("accessibility", "C", "C"),
    "button-name": ("accessibility", "C", "C"), "placeholder-text": ("layout", "C", "C"), "transition-all": ("motion", "C", "B"),
    "reduced-hidden": ("motion", "D", "D"), "reduced-animating": ("motion", "C", "C"), "focus-visible": ("accessibility", "C", "C"),
    "keyboard": ("accessibility", "D", "D"), "broken-link": ("accessibility", "C", "C"), "broken-anchor": ("accessibility", "C", "C"),
    "empty-submit": ("accessibility", "C", "C"), "form-feedback": ("accessibility", "C", "B"), "mobile-nav": ("responsive", "D", "D"),
}


def fail_lines(lines):
    for line in lines:
        print("FAIL " + line)
    print("RESULT  %s" % ("FAIL" if lines else "PASS"))
    return 1 if lines else 0


def to_letter(value):
    return LETTERS[max(0, min(4, math.floor(value + 0.5)))]


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, ValueError) as exc:
        return None, "%s cannot be read: %s" % (path, exc)


def skeleton(run):
    results, problem = load(run / "results.json")
    if problem:
        return fail_lines([problem])
    target = run / "grades.json"
    if target.exists():
        return fail_lines(["%s already exists" % target])
    blank = {"grade": "?", "reason": ""}
    shots = {s["id"]: {area: dict(blank) for area in GRADED} for s in results["shots"]}
    target.write_text(json.dumps({"summary": "", "top_fixes": [], "shots": shots}, indent=2) + "\n", encoding="utf-8")
    print("OK   wrote %s with %d shot(s) to grade" % (target, len(shots)))
    return fail_lines([])


def validate(results, grades, run):
    problems = []
    ids = {s["id"] for s in results["shots"]}
    given = grades.get("shots", {})
    problems += ["no grades for shot %s" % i for i in sorted(ids - set(given))]
    problems += ["grades for a shot that was not captured: %s" % i for i in sorted(set(given) - ids)]
    for sid in sorted(ids & set(given)):
        for area in GRADED:
            entry = given[sid].get(area)
            if not isinstance(entry, dict):
                problems.append("%s: no grade for %s" % (sid, area))
                continue
            allowed = set(POINTS) | ({"N/A"} if area == "imagery" else set())
            if entry.get("grade") not in allowed:
                problems.append("%s: %s has grade %r" % (sid, area, entry.get("grade")))
            if not str(entry.get("reason", "")).strip():
                problems.append("%s: %s has no reason" % (sid, area))
    if not str(grades.get("summary", "")).strip():
        problems.append("summary is empty")
    fixes = grades.get("top_fixes")
    if not isinstance(fixes, list) or not fixes or not all(str(x).strip() for x in fixes):
        problems.append("top_fixes must list at least one fix")
    for shot in results["shots"]:
        problems += ["missing image %s" % t for t in shot["tiles"] if not (run / t).is_file()]
        if not shot["tiles"]:
            problems.append("%s has no images" % shot["id"])
    return problems


def caps_for(findings):
    """area -> (best letter, ids of the checks that set it)."""
    out = {}
    for f in findings:
        rule = CAPS.get(f["id"])
        if not rule:
            continue
        area, on_fail, on_warn = rule
        cap = on_fail if f["severity"] == "fail" else on_warn
        if cap is None:
            continue
        best, why = out.get(area, ("A", []))
        if POINTS[cap] < POINTS[best]:
            best, why = cap, []
        if POINTS[cap] == POINTS[best]:
            why = why + [f["id"]]
        out[area] = (best, why)
    return out


def score(results, grades):
    """Final grades for every shot, plus per-route and whole-run grades."""
    scored = []
    for shot in results["shots"]:
        findings = shot["findings"] + results["route_findings"].get(shot["route"], [])
        caps = caps_for(findings)
        areas = {}
        for area in GRADED:
            entry = grades["shots"][shot["id"]][area]
            final = entry["grade"]
            row = {"name": AREA_NAMES[area], "grade": final, "reason": entry["reason"].strip(), "capped_from": None, "capped_by": []}
            if final != "N/A" and area in caps and POINTS[caps[area][0]] < POINTS[final]:
                row.update({"grade": caps[area][0], "capped_from": final, "capped_by": caps[area][1]})
            areas[area] = row
        if results["run"]["reduced_motion"] or "motion" in caps:
            best, why = caps.get("motion", ("A", []))
            reason = "Measured from the checks: " + ", ".join(sorted(set(why))) if why else "No motion problem measured."
            areas["motion"] = {"name": AREA_NAMES["motion"], "grade": best, "reason": reason, "capped_from": None, "capped_by": why}
        else:
            areas["motion"] = {"name": AREA_NAMES["motion"], "grade": "N/A", "reason": "The reduced-motion pass was skipped.", "capped_from": None, "capped_by": []}
        points = [POINTS[a["grade"]] for a in areas.values() if a["grade"] != "N/A"]
        mean = sum(points) / len(points)
        overall = to_letter(min(mean, min(points) + 1))
        scored.append(dict(shot, areas=areas, overall=overall, points=mean))
    routes = {}
    for route in results["routes"]:
        values = [s["points"] for s in scored if s["route"] == route]
        if values:
            routes[route] = to_letter(sum(values) / len(values))
    whole = to_letter(sum(s["points"] for s in scored) / len(scored))
    return scored, routes, whole


def embed(run, rel_path):
    data = base64.b64encode((run / rel_path).read_bytes()).decode("ascii")
    mime = "image/png" if rel_path.endswith(".png") else "image/jpeg"
    return "data:%s;base64,%s" % (mime, data)


def write_html(run, results, grades, scored, routes, whole):
    payload = {
        "run": results["run"], "overall": whole, "routes": routes, "summary": grades["summary"].strip(), "top_fixes": grades["top_fixes"],
        "notes": results["notes"], "errors": results["errors"], "skipped_routes": results["skipped_routes"], "external_links": results["external_links"],
        "route_findings": results["route_findings"],
        "extras": [dict(x, image=embed(run, x["image"])) for x in results["extras"]],
        "shots": [{
            "id": s["id"], "route": s["route"], "viewport": s["viewport"], "theme": s["theme"], "title": s["title"], "overall": s["overall"],
            "areas": s["areas"], "findings": s["findings"], "console": s["console"], "failed_requests": s["failed_requests"], "truncated": s["truncated"],
            "full": s["full"], "tiles": [embed(run, t) for t in s["tiles"]],
        } for s in scored],
    }
    # Page text ends up in this JSON, so nothing in it may be able to close the script block.
    data = json.dumps(payload).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    template = TEMPLATE.read_text(encoding="utf-8")
    if "__REPORT_DATA__" not in template:
        raise ValueError("the report template has no __REPORT_DATA__ marker")
    (run / "report.html").write_text(template.replace("__REPORT_DATA__", data), encoding="utf-8")


def write_summary(run, results, grades, scored, routes, whole):
    run_info = results["run"]
    lines = ["# Visual QA summary", "", "- Site: %s" % run_info["url"], "- Overall grade: **%s**" % whole,
             "- Screenshots graded: %d" % len(scored), "- Viewports: %s" % ", ".join(run_info["viewports"]),
             "- Themes: %s" % ", ".join(run_info["themes"]), "- Full report: `report.html`", "", grades["summary"].strip(), "", "## Grades by route", "",
             "| Route | Grade |", "| --- | --- |"]
    lines += ["| `%s` | %s |" % (route, grade) for route, grade in routes.items()]
    lines += ["", "## Fix these first", ""]
    lines += ["%d. %s" % (i, str(fix).strip()) for i, fix in enumerate(grades["top_fixes"], 1)]
    failing = {}
    for shot in scored:
        for f in shot["findings"]:
            if f["severity"] == "fail":
                failing.setdefault((f["id"], f["message"]), set()).add(shot["id"])
    for route, findings in results["route_findings"].items():
        for f in findings:
            if f["severity"] == "fail":
                failing.setdefault((f["id"], f["message"]), set()).add(route)
    lines += ["", "## Failing checks", ""]
    if failing:
        lines += ["| Check | Problem | Where |", "| --- | --- | --- |"]
        for (cid, message), where in sorted(failing.items()):
            places = sorted(where)
            shown = ", ".join("`%s`" % p for p in places[:3]) + (" and %d more" % (len(places) - 3) if len(places) > 3 else "")
            lines.append("| `%s` | %s | %s |" % (cid, message.replace("|", "/"), shown))
    else:
        lines.append("None.")
    capped = [(s["id"], a) for s in scored for a in s["areas"].values() if a["capped_from"]]
    if capped:
        lines += ["", "%d grade(s) were lowered by the measured checks." % len(capped)]
    extra = results["notes"] + ["Capture problem: %s" % e for e in results["errors"]]
    if results["skipped_routes"]:
        extra.append("Routes over the limit, not checked: %s" % ", ".join(results["skipped_routes"]))
    extra.append("Motion is graded from measurements only: hover and entrance animation cannot be judged from still images.")
    lines += ["", "## Notes", ""] + ["- %s" % n for n in extra]
    (run / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build(run):
    results, problem = load(run / "results.json")
    if problem:
        return fail_lines([problem])
    grades, problem = load(run / "grades.json")
    if problem:
        return fail_lines([problem])
    problems = validate(results, grades, run)
    if problems:
        return fail_lines(problems)
    scored, routes, whole = score(results, grades)
    write_html(run, results, grades, scored, routes, whole)
    write_summary(run, results, grades, scored, routes, whole)
    print("OK   overall grade %s across %d screenshot(s)" % (whole, len(scored)))
    print("OK   wrote %s and %s" % (run / "report.html", run / "summary.md"))
    return fail_lines([])


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade checks and report for the visual-qa skill.")
    ap.add_argument("--run", required=True, help="the capture folder")
    ap.add_argument("--skeleton", action="store_true", help="write an empty grades.json")
    args = ap.parse_args(argv)
    run = Path(args.run).resolve()
    if not run.is_dir():
        print("usage error: %s is not a folder" % run, file=sys.stderr)
        return 2
    return skeleton(run) if args.skeleton else build(run)


if __name__ == "__main__":
    sys.exit(main())
