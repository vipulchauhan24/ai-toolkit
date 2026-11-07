# AI Toolkit

A collection of Claude Code skills by Vipul Chauhan.

## Skills

| Skill                                                                                       | How to use it                                                                                                                                                                                                       |
| ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [design-system-builder](docs/skills/design-system-builder.md) | Ask Claude to "create a design system" and give it a product brief, screenshots, a brand palette, or a mix. It confirms a direction with you, then writes tokens, light and dark themes, component specs, and a contrast report. |
| [project-planner](docs/skills/project-planner.md)                                                 | Write a spec with `skills/project-planner/assets/spec-template.md`, then ask Claude to "plan this project" using that file. It asks about high-stakes decisions and splits the spec into phases that a coding agent builds one at a time.   |
| [doc-trimmer](docs/skills/doc-trimmer.md) | Ask Claude to "trim this" or "cut the noise" and give it pasted text, a file path, or a URL. It removes hedging, throat-clearing, padding, filler and repeated ideas, and keeps your facts, voice and structure. For a file it writes a `-cut` copy next to the original (`post.md` becomes `post-cut.md`) and never touches the original. It does not summarise or rewrite, and it leaves legal text, specs and fiction alone. |
| [ui-developer](docs/skills/ui-developer.md) | Ask Claude to "build this screen" or "restyle this". It builds the UI, or restyles existing UI, from a design system (Ember by default, or one you name) using only its tokens and utilities. It writes no custom CSS, builds the UI layer only (no APIs, databases or auth), runs an audit for raw values and unknown classes, and hands you a look-at list for each state. |
| [doc-reviewer](docs/skills/doc-reviewer.md) | Ask Claude to "poke holes in this" or "what could go wrong with this design" and give it pasted text, a file path, or a URL. It attacks the document and reports only holes: failure modes, unstated assumptions, skipped steps and unanswered questions, ranked `fatal`, `serious` or `sleeper`. Each finding quotes the text and ends with a question for the author. It gives no praise and no fixes, and it does not review code. |
| [frontend-react](docs/skills/frontend-react.md) | Ask Claude to "build this in React", "build this in Next.js" or "write this React component". It writes React and Next.js code to a fixed set of rules (components, hooks, state, effects, forms, performance, a typed data boundary, server and client components, tests), matches the project's own conventions first, and runs the typecheck, lint, tests, build and a React check script. It does not choose colors or component looks: name ui-developer too for that. It builds no APIs, databases or auth. |
| [backend-node](docs/skills/backend-node.md) | Ask Claude to "build this in Node.js", "write the service in Express" or "write the NestJS module". It writes TypeScript backend code to a fixed set of rules (types, errors, concurrency, configuration, services, entity classes from `schema.md`, boundaries, logging, security, tests), detects Express or NestJS from `package.json`, matches the project's own conventions first, and runs the typecheck, lint, tests, build and a Node check script. It stops with a Blocked report for any other framework or plain JavaScript. It writes no route handlers, controllers, queries, migrations or auth: it reports each as the typed boundary. |
| [backend-python](docs/skills/backend-python.md) | Ask Claude to "build this in Django", "write the FastAPI service" or "write the Python models". It writes Python backend code to a fixed set of rules (types, errors, concurrency, configuration, model classes from `schema.md`, services, boundaries, logging, security, tests), reads the Django or FastAPI rules only when the project depends on that framework, and runs the project's checks and a Python check script. It stops with a Blocked report for any other framework. It writes no views or route handlers, queries, migrations or auth: it reports each as the typed boundary. |
| [julia](docs/skills/julia.md) | Ask Claude to "write this in Julia", "model this as an LP with JuMP" or "analyse this data with DataFrames.jl". It writes Julia code to a fixed set of rules covering Oxygen service structure, DataFrames.jl, JuMP.jl with HiGHS.jl (LP and QP), model training with MLJ.jl and data analysis, reads `Project.toml` for the Julia version and dependencies, and runs `Pkg.test()` and a Julia check script. It writes no Oxygen route handlers, database access or auth: it reports each as the typed boundary. |

## Installing

The design-system-builder, project-planner, doc-trimmer, doc-reviewer, ui-developer, frontend-react, backend-node, backend-python and julia skills are published in the ai-toolkit Claude Code plugin. Add the marketplace and install it:

```text
claude plugin marketplace add vipulchauhan24/ai-toolkit
claude plugin install ai-toolkit@product-development
claude plugin update ai-toolkit@product-development
/reload-plugins
```

Invoke the skills with `/ai-toolkit:design-system-builder`, `/ai-toolkit:project-planner`, `/ai-toolkit:doc-trimmer`, `/ai-toolkit:doc-reviewer`, `/ai-toolkit:ui-developer`, `/ai-toolkit:frontend-react`, `/ai-toolkit:backend-node`, `/ai-toolkit:backend-python` and `/ai-toolkit:julia`, or let Claude pick them up from a matching prompt.

The language skills (backend-node, backend-python, julia) stop at the API and database boundaries until release 1.7.0; they report each boundary and name the skill that owns it.

## Using the skills with other providers

Each skill is a self-contained folder: a `SKILL.md` (the open Agent Skills format) plus its own `references/`, `scripts/` and `assets/`. Nothing is read from outside the folder, so you can copy or zip a single skill folder on its own. The skills live in `skills/`.

```bash
git clone https://github.com/vipulchauhan24/ai-toolkit.git
cd ai-toolkit/skills
```

### Other agents that support `SKILL.md`

Cursor, GitHub Copilot, opencode and similar tools load the same folder format from their own skills directory. Copy the skill folders there; see each tool's docs for the path.

### Chat apps and APIs without skill support

Chat apps and raw API calls have no skills loader, so supply the files yourself:

1. Paste the contents of `SKILL.md` as the system prompt, custom instructions, or the first message.
2. Attach the files the skill points to, from its folder:
   - project-planner: `references/project-planner-rules.md`, `references/markdown-rules.md`, `references/architecture-patterns.md`, and `assets/spec-template.md`
   - doc-trimmer: `references/markdown-rules.md`
   - design-system-builder: `references/tokens.example.css`
   - doc-reviewer: none, `SKILL.md` is enough
   - ui-developer: `references/app-screens.md`, `copy.md` and `layout.md`, `scripts/audit_ui.py`, and `references/phase-document.md` and `references/restyle.md` when needed
   - project-planner also pins the coding pattern (`Pattern:` line) in Phase 1; the language skills read it from the phase document, else from the codebase.
   - frontend-react: `references/react-rules.md`, `references/architecture-patterns.md`, `references/nextjs-rules.md` (Next.js only), `references/react-performance-guidelines.md` (performance work only) and `scripts/check_react.py`
   - backend-node: the whole `skills/backend-node/` folder (`references/node-rules.md`, `express-rules.md`, `nestjs-rules.md`, `architecture-patterns.md`, `examples.md` and `scripts/check_node.py`)
   - backend-python: the whole `skills/backend-python/` folder (`references/python-rules.md`, `django-rules.md`, `fastapi-rules.md`, `architecture-patterns.md`, `examples.md` and `scripts/check_python.py`)
   - julia: the whole `skills/julia/` folder (`references/julia-rules.md`, `architecture-patterns.md`, `examples.md` and `scripts/check_julia.py`)
3. Send your request (a spec to plan, a brief, screenshots or palette to build from, text to trim, or a document to review).

### What to expect outside Claude Code

- design-system-builder ends by running `./scripts/check_contrast.sh <theme-name>` and `python3 -I scripts/build_tokens_json.py <theme-name>`. This needs an agent with shell access and Python. In a plain chat, run the scripts yourself on the generated folder, or the contrast check is skipped and `tokens.json` is not generated.
- doc-trimmer fetches URLs with `curl` and writes the `-cut` file, so both need an agent with shell and file access. In a plain chat, paste the text and copy the result yourself.
- doc-reviewer fetches URLs with `curl` and reads files, so it needs an agent with shell and file access for those inputs. In a plain chat, paste the document text.
- Screenshot mode needs a model that accepts image input.
- frontend-react runs the project's own typecheck, lint, tests and build and `scripts/check_react.py` with Python 3, so it needs an agent with shell access. Python 3 is required: without it the skill stops with an error.
- backend-node, backend-python and julia run the project's own checks and their `scripts/check_*.py` with Python 3, so they need an agent with shell access. Python 3 is required: without it the skill stops with a Blocked report. They stop at the API and database boundaries until release 1.7.0.
- ui-developer fetches the design system with `git` and runs `scripts/audit_ui.py` with Python 3, so it needs an agent with shell access. Without Python it falls back to manual searches.
- The `/ai-toolkit:...` commands are Claude Code only. Elsewhere, trigger the skills with a prompt.

## Repository Layout

The repository root is the `ai-toolkit` plugin.

| Path              | Contents                                                                                                       |
| ----------------- | -------------------------------------------------------------------------------------------------------------- |
| `.claude-plugin/` | The marketplace manifest (`marketplace.json`) and the plugin manifest (`plugin.json`).                         |
| `skills/`         | One self-contained folder per skill (design-system-builder, project-planner, doc-trimmer, doc-reviewer, ui-developer, frontend-react, backend-node, backend-python, julia): `SKILL.md`, plus `references/`, `scripts/` and `assets/` where needed.   |
| `templates/`      | `language-skill-template/`, a copy-and-fill starting point for a new language skill, with a checklist. It is not a skill and the plugin does not load it. |
| `agents/`         | `skill-runner`, a generic subagent that runs named skills in its own context and writes a report file.         |
| `docs/skills/`    | One guide per skill for human readers (usage, examples, customizing). Skills do not read these.                |
| `scripts/`        | Repository tooling. `shared_files.json` lists every file copied into several skills. `check_shared_files.py` fails if a copy has drifted, and `--sync` copies the canonical file over the others.      |
| `tests/`          | Fixtures, model-run cases (`cases/`), the test harness (`run.py`), per-skill test specs (`<skill>.md`) and `runs/` run logs. See [Testing Skills and Rules](#testing-skills-and-rules). |

Files used by more than one skill are copied into each skill folder, and `scripts/shared_files.json` lists them (for example `markdown-rules.md` and `architecture-patterns.md`). The first path in each entry is the canonical copy. Edit it, run `python3 scripts/check_shared_files.py --sync`, then run the script without `--sync` to confirm.

## Releasing

Run these steps from the repository root before each version bump. The checks need Python 3.9 or later and run on Linux and macOS. Steps 1 to 4 and 6 need no network and no model. Every step prints nothing, `OK <version>` or `done`, unless the step says otherwise; any other line is a failure to fix.

### Step 1: Version match

Prints `OK <version>`. Run it first: a JSON error in a manifest stops here instead of in step 5.

```bash
python3 -I - <<'PY'
import json
a = json.load(open(".claude-plugin/plugin.json"))["version"]
b = json.load(open(".claude-plugin/marketplace.json"))["plugins"][0]["version"]
assert a == b, (a, b)
print("OK", a)
PY
```

### Step 2: SKILL.md length, skill folder shape and shared files

Prints nothing. Every `SKILL.md` is under 500 lines and 5,000 words, no skill folder holds a `README.md`, and `scripts/check_shared_files.py` has no `MISSING` or `DIFFERS` line.

```bash
for f in skills/*/SKILL.md; do n=$(wc -l < "$f"); w=$(wc -w < "$f"); [ "$n" -lt 500 ] || echo "TOO LONG: $f $n lines"; [ "$w" -lt 5000 ] || echo "TOO MANY WORDS: $f $w"; done
find skills -iname 'README*' | sed 's/^/README IN SKILL FOLDER: /'
python3 -I scripts/check_shared_files.py | grep -E '^(MISSING|DIFFERS)'
```

### Step 3: Contents lists

Prints only `done`. A rules file over 100 lines needs a `## Contents` list that matches its `##` headings.

```bash
python3 -I - <<'PY'
import glob, re
RULES = r"(react|nextjs|node|express|nestjs|python|django|fastapi|julia|api|postgres|mysql|mongodb)-rules\.md$|architecture-patterns\.md$|react-performance-guidelines\.md$"
for f in sorted(g for g in glob.glob("skills/*/references/*.md") if re.search(RULES, g)):
    t = open(f).read().split("\n")
    if len(t) <= 100:
        continue
    if "## Contents" not in t:
        print("NO CONTENTS", f)
        continue
    heads = [re.sub(r"^\d+\.\s*", "", l[3:]).strip() for l in t if l.startswith("## ") and l != "## Contents"]
    items = []
    for l in t[t.index("## Contents") + 1:]:
        if not l.strip():
            if items:
                break
            continue
        m = re.match(r"\d+\.\s*(.*)", l)
        if not m:
            break
        items.append(m.group(1).strip())
    if items != heads:
        print("MISMATCH", f)
print("done")
PY
```

### Step 4: Fixtures

The last line must read `fixtures status=0`. Every skill that has fixtures under `tests/fixtures/<skill>/<flag-set>/` is covered, so later skills need no change here. Keep one check script (`check_*.py` or `audit_*.py`) per skill.

```bash
status=0
for clean in tests/fixtures/*/*/clean; do
  [ -d "$clean" ] || continue
  set_dir=$(dirname "$clean"); fl=$(basename "$set_dir"); skill=$(basename "$(dirname "$set_dir")")
  script=$(ls skills/$skill/scripts/check_*.py skills/$skill/scripts/audit_*.py 2>/dev/null)
  flag=""; [ "$fl" != base ] && flag="--$fl"
  python3 -I "$script" $flag $(find "$clean" -type f | sort) > /dev/null || { echo "CLEAN FAILS: $skill $fl"; status=1; }
  for f in $(find "$set_dir/seeded" -type f | sort); do
    python3 -I "$script" $flag "$f" | grep -q '^FAIL' || { echo "NOT FAILING: $f"; status=1; }
  done
done
echo "fixtures status=$status"
```

### Step 5: Local install

from a clean profile (a temporary `HOME`, so your real plugins are untouched). It must exit 0, and `claude plugin list` must show `ai-toolkit` at the version from step 1. Needs the `claude` CLI. If a `claude plugin` subcommand does not exist in your version, stop and report it.

```bash
tmp=$(mktemp -d); HOME="$tmp" claude plugin marketplace add "$(pwd)" && HOME="$tmp" claude plugin install ai-toolkit@product-development && HOME="$tmp" claude plugin list
```

### Step 6: Static and script suites

(offline, a few seconds, no model). Each prints `RESULT  PASS` and no line that starts with `FAIL` or `XPASS`. `WARN` and `XFAIL` lines are listed in the release notes and do not block.

```bash
python3 -I tests/run.py static && python3 -I tests/run.py scripts
```

### Step 7: Model-run cases

Needs the `claude` CLI, uses tokens and takes several minutes. It prints `RESULT  PASS` and writes `tests/runs/model-cases-<version>.md`. Run the `network` tier as well when Ember or `ui-developer` changed. A failing case is rerun once automatically; a second failure means the skill text is unclear, so fix the skill, not the case.

```bash
python3 tests/run.py cases --tier slow
python3 tests/run.py cases --tier network
```

### Step 8: Merge, tag, push (by hand)

Merge the release PR, then:

```bash
git tag -a v<version> -m "ai-toolkit <version>"
git push origin v<version>
```

Save the output of steps 1 to 5 in `tests/runs/release-process-<version>.md` for the release notes.

## Versioning

The plugin follows semantic versioning (`MAJOR.MINOR.PATCH`). `plugin.json` and `marketplace.json` always carry the same version.

- **Major:** a breaking change. Breaking means a skill rename or removal, a rules file path move, or a check-script flag change.
- **Minor:** a new skill, rules file or check script, or a new behavior that breaks nothing.
- **Patch:** a fix or a wording change.

Each release is a git tag `vX.Y.Z`. To roll back, revert the release PR and ship the next patch version. Report problems at <https://github.com/vipulchauhan24/ai-toolkit/issues>.

## Getting Help

Open a GitHub issue at <https://github.com/vipulchauhan24/ai-toolkit/issues>. Include the skill name, the plugin version (`claude plugin list`), the prompt you gave and what you expected.

## Testing the Check Scripts

Each skill with a check script has fixtures under `tests/fixtures/<skill>/<flag-set>/`:

```text
tests/fixtures/frontend-react/base/
  clean/        files the script must pass
  seeded/       one file per FAIL rule, each holding that one violation
  expected.json seeded file -> regex its FAIL line must match, the clean file count, and xfail
```

`<flag-set>` is `base` for a plain run, or the name of a flag (`next` runs the script with `--next`). Run `python3 -I tests/run.py scripts`. A clean fixture must exit 0. A seeded fixture must exit 1 with a `FAIL` line that matches its entry in `expected.json`, and with no other `FAIL` line. A rule that is known not to fire goes in `xfail` with a reason and prints `XFAIL`; once it fires the run prints `XPASS` and fails until the entry is removed.

To add a rule: add a seeded file, add its pattern to `expected.json`, and run the command. A new script under `skills/*/scripts/` needs an entry in `SCRIPT_COVERAGE` in `tests/run.py` or the static layer fails with `script has a test`. Keep one check script per skill.

## Testing Skills and Rules

Three layers, all driven by `tests/run.py`:

```bash
python3 -I tests/run.py static
python3 -I tests/run.py scripts
python3 tests/run.py cases --tier slow
```

- `static` checks manifests, front matter, referenced paths, folder shape, contents lists, shared files and that every skill, agent and rules file is covered by a case. Offline, no model.
- `scripts` runs the check scripts against the fixtures (see above). Offline, no model.
- `cases` runs skills and agents through `claude -p` with the plugin loaded from this checkout, then asserts on the output and the files written. **Only this layer needs the `claude` CLI and costs tokens.** Use `cases --list` to list the cases, `--tier fast|slow|network` to pick a tier and `--case <id>` to run one. Raw transcripts go to `tests/runs/.cases/`, which git ignores.

After changing a skill or a rules file, run `static`, then the cases that list that file in `covers`. To add a case, write it in `tests/cases/<skill>.json`, derived from a section of `tests/<skill>.md` named in its `source` key. The format is in [tests/README.md](tests/README.md).

## License

MIT. See [LICENSE](LICENSE).
