# Tests

Tests for the skills, the agent and the rules files in this plugin. One harness, `run.py`, with three layers. It needs Python 3.9 or later and uses only the standard library. Run every command from the repository root.

| Layer     | Command                                  | Needs                | Time        | What it proves                                                                                                   |
| --------- | ---------------------------------------- | -------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------- |
| `static`  | `python3 -I tests/run.py static`         | Python               | seconds     | Skills, agents, rules and manifests are well formed and point at files that exist. Every skill and rule has a case. |
| `scripts` | `python3 -I tests/run.py scripts`        | Python               | seconds     | Each check script passes its clean fixtures and fails each seeded one with the expected message.                |
| `cases`   | `python3 tests/run.py cases`             | `claude` CLI, tokens | minutes     | The model, given the skill, does what the skill says: right files read, right output, right files written.     |

`python3 tests/run.py all` runs the three in order. Every line is `PASS`, `FAIL`, `XFAIL`, `XPASS` or `WARN`, and the last line is `RESULT  PASS` or `RESULT  FAIL`. The exit code is 1 on any `FAIL` or `XPASS`.

## static

Checks, among others:

- Every `SKILL.md` has front matter, `name` equals the folder name, `description` is 1 to 1024 characters, and the file is under 500 lines.
- Every agent has `name`, `description` and `tools`.
- Paths written in skills, agents and rules (`../../rules/...`, `references/...`, `scripts/...`) exist.
- Every script parses as Python 3.9 or as bash, and has an entry in `SCRIPT_COVERAGE` in `run.py`.
- Rules files over 100 lines in `rules/coding/` and `rules/database/` have a `## Contents` list that matches their headings. Other folders print `WARN`.
- Every rules file is mentioned by a skill, an agent or another rules file.
- The default-pattern table in `architecture-patterns.md` has 7 rows.
- Every skill, agent and non-empty rules file appears in the `covers` list of at least one case.

## scripts

Fixtures are in `tests/fixtures/<skill>/<flag-set>/`:

```text
frontend-react/base/   clean/ (files that must pass)   seeded/ (one violation each)   expected.json
frontend-react/next/   same, run with --next
ui-developer/base/     same
design-system-builder/ clean/Mini and seeded/MiniLowContrast (tokens.css for the contrast check)
```

`expected.json` maps each seeded file to a pattern that must appear in its `FAIL` line, so a file that fails for the wrong reason is caught. `xfail` lists known defects: the test prints `XFAIL`, and prints `XPASS` (a failure) once the defect is fixed, so the entry cannot be forgotten. Today it lists the `@ts-ignore` rule in `check_react.py`, which never fires.

To add a seeded case, add the file, add its message pattern to `expected.json`, and run `scripts`.

## cases

Each case copies a fixture to a temporary directory, runs `claude -p` there with this checkout loaded as the plugin (`--plugin-dir`), and asserts on the transcript and the files. The skill under test is the one in the checkout, not an installed copy.

```bash
python3 tests/run.py cases --list                    # list cases and what each covers
python3 tests/run.py cases --tier fast               # cases that take about a minute each
python3 tests/run.py cases --case trimmer-noisy      # one case
python3 tests/run.py cases --tier network --jobs 1   # includes the case that fetches Ember from GitHub
```

Options: `--tier fast|slow|network` (highest tier to run, default `slow`), `--case ID` (repeatable), `--jobs N` (default 2), `--model NAME`, `--log-dir DIR`, `--dry-run`.

Transcripts (`<id>.stream.jsonl`) and the final output (`<id>.txt`) go to `tests/runs/.cases/`, which git ignores. Copy the result lines into `tests/runs/<name>.md` when you want to keep a record.

### Reading a result

- `invoked skill X` or `invoked agent X` failing: the model did not use the skill. Check the skill's `description` (the trigger words), not the case.
- `read a file matching ...` failing: the skill did not read a rules file it should have. Check the Preflight text in `SKILL.md`.
- `output matches ...` failing: compare `tests/runs/.cases/<id>.txt` with the skill's output format.
- A case that fails once may be model variation. Rerun it with `--case <id>`. A second failure means the skill text is unclear: fix the skill. Do not weaken the case.

### Case format

Cases are in `tests/cases/<skill>.json`, a list of objects:

| Key                          | Meaning                                                                                                   |
| ---------------------------- | --------------------------------------------------------------------------------------------------------- |
| `id`, `tier`, `fixture`      | Unique name, `fast` / `slow` / `network`, and a folder under `tests/fixtures/`                            |
| `covers`                     | Repository paths the case exercises: `skills/<name>`, `agents/<file>`, `rules/...`, `templates/...`       |
| `prompt`, `tools`, `timeout` | The message, the `--allowedTools` string (default `Read,Glob,Grep,Skill`), seconds before the run is killed |
| `skills`, `agents`, `reads`  | Skill calls, Agent calls and file reads (regex on the path) the transcript must contain                   |
| `must`, `must_not`           | Regexes the final output must and must not match                                                          |
| `files`                      | A glob in the working copy mapped to `exists`, `must` and `must_not` (regexes on its contents)            |
| `no_files`, `unchanged`      | Globs that must match nothing, and files whose hash must not change                                       |
| `post`                       | Shell commands run in the working copy that must exit 0. `{repo}` is the repository root                  |

To add a case:

1. Put the smallest input that triggers the behavior in `tests/fixtures/`.
2. Add the case to the skill's JSON file. List every skill and rules file it exercises in `covers`.
3. Assert only what the skill's text requires: a required line, a file written, a file left unchanged, a rules file read. Do not match whole outputs.
4. Run `python3 -I tests/run.py static`, then `python3 tests/run.py cases --case <id>`.

When you add a skill, agent or rules file, `static` fails until a case covers it. When you add a script under `skills/*/scripts/`, add it to `SCRIPT_COVERAGE`.

## What is not tested

- Output quality. Cases check structure and required behavior, not whether a review is insightful.
- Skills that do not exist yet. Each later skill phase adds its own fixtures and cases.
- `rules/coding/api-rules.md`, which is empty until phase 11. `static` prints `WARN` for it.
