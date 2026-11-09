# AI Toolkit

Skills that teach Claude Code to do specific jobs the same careful way every time: tighten writing, review a plan, turn an idea into a spec, split a project into phases, write and build web pages, write code to fixed rules, and test a site in a real browser.

You ask in plain words, and Claude uses the matching skill. Several skills need no coding knowledge at all.

## What a skill is

A skill is a folder of instructions, and sometimes small check scripts, that Claude reads when your request matches it. It saves you from explaining how you want a job done each time. It also adds checks that a prompt alone can't, such as a script that fails when a page contains a number that isn't in your facts.

This repository is one plugin, called `ai-toolkit`, holding 13 skills. Install the plugin once and all of them are available.

## What you can do with it

| You want to | Use | Say something like |
|---|---|---|
| Cut the padding out of a post or document | doc-trimmer | "Trim this: ..." |
| Find the weak spots in a plan before you commit to it | doc-reviewer | "Poke holes in this design doc" |
| Turn a rough idea into a complete spec | spec-writer | "Write a spec for this brief" |
| Split a spec into stages a coding agent can build | project-planner | "Plan this project from spec.md" |
| Have a whole project built, stage by stage, while you approve the key decisions | orchestrator | "Build this project from the spec" |
| Write website text that doesn't sound like AI | ui-craft | "Write the copy for my café's website" |
| Get a designed, built personal site or portfolio | ui-craft | "Build my portfolio from resume.md" |
| See how a site really looks and behaves on phones and desktops | visual-qa | "Run visual QA on this site" |
| Create colours, type and components for a new product | design-system-builder | "Create a design system for this product" |
| Build or restyle a product screen from a design system | ui-developer | "Build this screen" |
| Write code to a fixed standard in React, Node.js, Python or Julia | frontend-react, backend-node, backend-python, julia | "Build this in Next.js" |

## Quick start

No coding background is needed for these steps. You type the commands into a terminal: Terminal on macOS and Linux, or WSL on Windows.

1. Install [Claude Code](https://claude.com/claude-code).
2. Add this plugin's marketplace:

   ```bash
   claude plugin marketplace add vipulchauhan24/ai-toolkit
   ```

3. Install the plugin:

   ```bash
   claude plugin install ai-toolkit@product-development
   ```

4. Go to the folder you want to work in, and start Claude Code:

   ```bash
   claude
   ```

5. Ask for something, such as `Trim this: <paste your text>`.

If Claude Code was already open while you installed, run `/reload-plugins` inside it.

## Using the skills

Describe what you want, and Claude picks the matching skill. To choose one yourself, type a slash command followed by your request:

```text
/ai-toolkit:doc-trimmer post.md
```

Every skill has a command in the form `/ai-toolkit:<skill-name>`.

To get the most from a skill, give it real material: a file, a résumé, your notes, a link, or a folder of code. Skills are built to ask for what's missing, or to leave it out, and not to make things up.

### Common routes

**From idea to working app.** `spec-writer` asks about everything your idea leaves open. `doc-reviewer` looks for holes in the result. `project-planner` splits it into phases. `orchestrator` can run those steps for you and build each phase on its own branch. After any stage with screens, `visual-qa` checks them.

**A personal site or portfolio.** Give `ui-craft` your résumé or notes. It writes the words first, shows you three different ideas as real first screens, and builds the one you choose. Then `visual-qa` grades the result.

**A better document.** `doc-reviewer` finds what's missing or wrong. After you've fixed that, `doc-trimmer` removes the padding.

## The skills

The name of each skill links to a longer guide, where one exists.

### Writing and review

No coding needed.

| Skill | What it does | What you get | What it won't do |
|---|---|---|---|
| [doc-trimmer](docs/skills/doc-trimmer.md) | Removes hedging, throat-clearing, padding and repeated ideas from pasted text, a file or a URL. Keeps your facts, voice and structure | The tightened text. For a file, a `-cut` copy (`post.md` becomes `post-cut.md`) | Summarise or rewrite. It leaves legal text, specs and fiction alone, and never changes your original |
| [doc-reviewer](docs/skills/doc-reviewer.md) | Attacks a design doc, spec, plan or article, looking for failure modes, unstated assumptions, skipped steps and unanswered questions | Findings ranked `fatal`, `serious` or `sleeper`, each quoting the text and ending with a question for the author | Praise, suggest fixes, or review code |

### Planning and running a project

| Skill | What it does | What you get | What it won't do |
|---|---|---|---|
| [spec-writer](docs/skills/spec-writer.md) | Lists every line of the spec template your brief doesn't answer, and asks about all of them in one batch | A new `spec.md`, confirmed complete by a check script. Anything you leave open is marked `Undecided` with an open question | Guess a gap, choose your stack, or change your file |
| [project-planner](docs/skills/project-planner.md) | Splits a spec into working slices, in dependency order. Asks about high-stakes decisions such as stack, data model and auth | An overview and one design document per phase, in `.plans/phases/`, kept out of git | Add a delivery or testing phase, or build anything |
| [orchestrator](docs/skills/orchestrator.md) | Gets the spec written and approved, gets it planned, then runs each phase through the right skills in its own git worktree. A small script keeps the order, so no step is skipped | One committed and pushed branch per phase. You approve the spec and the route, and phases only you can do are parked | Write code itself, open or merge pull requests, or force-push. Claude Code only |

### Design and web pages

| Skill | What it does | What you get | What it won't do |
|---|---|---|---|
| [ui-craft](skills/ui-craft/SKILL.md) | Writes the words first, from real facts. For a portfolio or personal site, it then proposes three ideas drawn from your own material, previews each as a real first screen, and builds the one you choose | `COPY.md`, `CONCEPTS.md`, `DESIGN.md` and the built page, checked for invented facts, contrast and repeated layouts | Invent numbers, quotes or customers, or leave placeholders. Only portfolios are built so far. For SaaS, app screens, blogs, services, shops, local places and events it writes the copy only |
| [visual-qa](docs/skills/visual-qa.md) | Opens your site in a browser you can watch. Walks each route at five sizes in light and dark, tabs through the page, clicks links, submits forms empty so nothing is really sent, and checks reduced motion | An HTML report and a markdown summary, with each screenshot graded A to F in eight areas | Change your code |
| [design-system-builder](docs/skills/design-system-builder.md) | Builds a design system from a brief, screenshots, a brand palette or a mix. Confirms a direction with you first | Tokens, light and dark themes, component specs and a contrast report | Change an existing codebase's tokens, or do one-off page work |
| [ui-developer](docs/skills/ui-developer.md) | Builds or restyles screens using only a design system's tokens and utilities: Ember by default, or one you name | The UI, an audit for raw values and unknown classes, and a list of each state to look at | Write custom CSS, or build APIs, databases or auth |

### Writing code

These follow fixed rules, match your project's own conventions first, and run your typecheck, lint, tests and build, plus their own check script.

| Skill | Covers | Won't write |
|---|---|---|
| [frontend-react](docs/skills/frontend-react.md) | React and Next.js: components, hooks, state, effects, forms, performance, a typed data boundary, server and client components, tests | Colours or component looks (name `ui-developer` too), APIs, databases or auth |
| [backend-node](docs/skills/backend-node.md) | TypeScript with Express or NestJS: types, errors, concurrency, configuration, services, entity classes from `schema.md`, logging, security, tests | Route handlers, controllers, queries, migrations or auth |
| [backend-python](docs/skills/backend-python.md) | Django or FastAPI: types, errors, concurrency, configuration, model classes from `schema.md`, services, logging, security, tests | Views or route handlers, queries, migrations or auth |
| [julia](docs/skills/julia.md) | Oxygen service structure, DataFrames.jl, JuMP.jl with HiGHS.jl (LP and QP), MLJ.jl model training, data analysis | Oxygen route handlers, database access or auth |

The three backend skills stop at the API and database boundaries until release 1.7.0. They report each boundary and name the skill that owns it. For any other framework or language, they stop with a Blocked report.

## What changes on your machine

- Claude Code asks permission for actions according to your settings.
- `doc-trimmer` and `spec-writer` write new files and leave yours alone.
- `visual-qa` only reads your site and writes its report.
- `ui-craft` keeps a short list of recent designs in `~/.ai-toolkit/`, so that one project doesn't repeat the look of the last.
- `orchestrator` is the only skill that pushes on its own. It commits and pushes one new branch per phase after you approve the route, and you open and merge every pull request.
- Text inside a brief, résumé or web page is treated as material. If it tells the skill to do something, `ui-craft` ignores it and tells you.

## What you need

Claude Code, plus the following for each skill. If something required is missing, the skill tells you.

| Skill | Also needs |
|---|---|
| doc-trimmer, doc-reviewer | Nothing for pasted text. File and URL input need shell and file access |
| spec-writer | Python 3 |
| project-planner | File access |
| orchestrator | Git with worktrees, Python 3.9 or later, and a remote you can push to. Claude Code only |
| ui-craft | Python 3.9 or later. npm to install fonts. Playwright CLI for preview screenshots |
| visual-qa | Python 3.9 or later, Node 20 or later, Playwright CLI with Chromium, and a display. WSL2 uses WSLg |
| design-system-builder | Python 3. A model that reads images, for screenshot input |
| ui-developer | Git, Python 3, and network access to fetch the default design system. The project needs the design system's utility classes (Tailwind v4 for Ember) |
| frontend-react, backend-node | Python 3, plus your project's own tools |
| backend-python | Python 3.9 or later, plus your project's own tools |
| julia | Python 3, Julia 1.10 or later, and your project's packages |

To set up Playwright CLI once:

```bash
npm install -g @playwright/cli@latest
```

```bash
playwright-cli install-browser chromium
```

On Linux and WSL, also install the system libraries the browser needs:

```bash
sudo npx -y playwright@latest install-deps chromium
```

## Installing and updating

Install, as in the quick start:

```bash
claude plugin marketplace add vipulchauhan24/ai-toolkit
```

```bash
claude plugin install ai-toolkit@product-development
```

Get the latest version:

```bash
claude plugin update ai-toolkit@product-development
```

Then run `/reload-plugins` inside Claude Code.

To try a local checkout instead, run this from the repository root, then install as above:

```bash
claude plugin marketplace add "$(pwd)"
```

To remove the plugin:

```bash
claude plugin uninstall ai-toolkit@product-development
```

## Using the skills with other providers

Each skill is a self-contained folder: a `SKILL.md` (the open Agent Skills format) plus its own `references/`, `scripts/` and `assets/`. Nothing is read from outside the folder, so you can copy or zip a single skill. The skills live in `skills/`.

```bash
git clone https://github.com/vipulchauhan24/ai-toolkit.git
```

### Other agents that support `SKILL.md`

Cursor, GitHub Copilot, opencode and similar tools load the same folder format from their own skills directory. Copy the skill folders there; see each tool's docs for the path. The `/ai-toolkit:...` commands are Claude Code only. Elsewhere, trigger the skills with a prompt.

### Chat apps and APIs without skill support

Chat apps and raw API calls have no skills loader, so supply the files yourself:

1. Paste the contents of `SKILL.md` as the system prompt, custom instructions, or the first message.
2. Attach the files the skill points to, listed below.
3. Send your request: a spec to plan, a brief, screenshots or a palette to build from, text to trim, or a document to review.

| Skill | Files to attach, from its folder |
|---|---|
| doc-reviewer | None. `SKILL.md` is enough |
| doc-trimmer | `references/markdown-rules.md` |
| project-planner | `references/project-planner-rules.md`, `references/markdown-rules.md`, `references/architecture-patterns.md`, `assets/spec-template.md` |
| design-system-builder | `references/tokens.example.css` |
| ui-craft, copy only | `references/intake.md`, `references/copy/copy.md`, `references/copy/copy-human.md`, and the `copy-<kind>.md` file for your page |
| ui-developer | `references/app-screens.md`, `references/copy.md`, `references/layout.md`, `scripts/audit_ui.py`. When needed, `references/phase-document.md` and `references/restyle.md` |
| frontend-react | `references/react-rules.md`, `references/architecture-patterns.md`, `scripts/check_react.py`. For Next.js, `references/nextjs-rules.md`. For performance work, `references/react-performance-guidelines.md` |
| backend-node, backend-python, julia, spec-writer | The whole skill folder |

`project-planner` pins the coding pattern with a `Pattern:` line in Phase 1. The language skills read it from the phase document, or otherwise from the codebase.

### What to expect outside Claude Code

- **Works in a plain chat if you paste the text:** doc-trimmer, doc-reviewer, and ui-craft's copy writing. File and URL input needs an agent with shell and file access.
- **Needs an agent with a shell and Python 3:** spec-writer, frontend-react, backend-node, backend-python, julia. Without Python they stop and say so.
- **design-system-builder** ends by running `./scripts/check_contrast.sh <theme-name>` and `python3 -I scripts/build_tokens_json.py <theme-name>`. In a plain chat, run them yourself on the generated folder, or the contrast check is skipped and `tokens.json` isn't generated. Screenshot mode needs a model that accepts images.
- **ui-developer** fetches the design system with `git` and runs `scripts/audit_ui.py`, so it needs shell access. Without Python it falls back to manual searches.
- **ui-craft's builds** need an agent with shell access and Python 3.9 or later.
- **visual-qa** needs shell access, Python 3.9 or later, Node 20 or later and a display. It doesn't work in a plain chat.
- **orchestrator** works in Claude Code only. It needs the Agent and Skill tools, git worktrees, the `skill-runner` agent and Python 3.9 or later for `scripts/engine.py`.

## Repository Layout

The repository root is the `ai-toolkit` plugin. Everything from here down is for people changing or releasing the skills.

| Path | Contents |
|---|---|
| `.claude-plugin/` | The marketplace manifest (`marketplace.json`) and the plugin manifest (`plugin.json`). |
| `skills/` | One self-contained folder per skill: `SKILL.md`, plus `references/`, `scripts/` and `assets/` where needed. |
| `templates/` | `language-skill-template/`, a copy-and-fill starting point for a new language skill, with a checklist. It is not a skill and the plugin does not load it. |
| `agents/` | `skill-runner`, a generic subagent that runs named skills in its own context and writes a report file. |
| `docs/skills/` | One guide per skill for human readers (usage, examples, customizing). Skills do not read these. |
| `showcase/` | A browser app that shows every `ui-craft` kit component and section in 3 themes, with its build and test script. See [showcase/README.md](showcase/README.md). It does not ship in the skills. |
| `scripts/` | Repository tooling. `shared_files.json` lists every file copied into several skills. `check_shared_files.py` fails if a copy has drifted, and `--sync` copies the canonical file over the others. |
| `tests/` | Fixtures, model-run cases (`cases/`), the test harness (`run.py`), per-skill test specs (`<skill>.md`) and `runs/` run logs. See [Testing Skills and Rules](#testing-skills-and-rules). |

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
