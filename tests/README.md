# Tests

Three layers, all driven by one file, `tests/run.py`, which uses only the Python standard library (Python 3.9 or later, Linux and macOS).

```bash
python3 -I tests/run.py static
python3 -I tests/run.py scripts
python3 tests/run.py cases --tier slow
```

| Layer     | What it proves                                                                                                                                                       | Needs the `claude` CLI and tokens |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| `static`  | Manifests agree, every skill and agent has valid front matter, every path a `SKILL.md` names exists, folder shape, `SKILL.md` length, contents lists, shared files match, every skill, agent and rules file is covered by a case | No                                |
| `scripts` | Each check script passes its clean fixtures and fails each seeded fixture with the expected message                                                                  | No                                |
| `cases`   | A skill or agent loads, reads its rules and makes the model behave as its text says                                                                                  | **Yes**                           |

A pass means the command prints `RESULT  PASS`. `FAIL` and `XPASS` lines fail a run. `WARN` and `XFAIL` lines do not, but go in the release notes. `static` and `scripts` finish in seconds, write nothing into the repository and print the same lines on every run.

## Source of the cases

`tests/<skill>.md` is the human-readable source: 10 should-trigger queries, 10 should-not queries and Given / When / Then checks per skill (and for the `skill-runner` agent). The triggering queries are checked by hand in a fresh Claude Code session, as the Anthropic skills guide describes: paste each query without naming the skill and pass if the skill loads (or, for should-not, does not). Re-run them after any change to a skill's `description`.

The `claude -p` cases in `tests/cases/*.json` are derived from those files. Each carries a `source` key that names the section it came from, for example `doc-trimmer.md: Functional / File input`. The static layer fails when a `source` names a heading or label that does not exist.

## Running the model cases

```bash
python3 tests/run.py cases --list                 # list the cases
python3 tests/run.py cases --tier fast            # fast only
python3 tests/run.py cases --tier slow            # fast and slow (the default)
python3 tests/run.py cases --tier network         # needs internet, for Ember
python3 tests/run.py cases --case doc-trimmer-id  # one case, no log written
```

- Tiers: `fast` (under about a minute each), `slow` (several minutes) and `network`. Run before a release and after any `SKILL.md` or rules change, not on every commit.
- Each case runs in a temporary copy of its fixture, so fixtures are never modified, and `claude -p` is started with `--plugin-dir` pointing at this checkout, so the skill under test is the one in the checkout and not an installed copy.
- A failing case is rerun once (`--no-retry` turns that off). The log records both attempts. A second failure means the skill text is unclear: fix the skill, do not weaken the case.
- Raw transcripts go to `tests/runs/.cases/`, which git ignores. A tier run writes `tests/runs/model-cases-<version>.md`, including the wall-clock time (`--jobs N` sets the parallel jobs, default 2; `--no-log` skips the log).
- Without the `claude` CLI the layer prints `FAIL claude CLI is on PATH` and runs nothing else.

## Case format

`tests/cases/<skill>.json` holds a list of objects:

| Key                         | Meaning                                                                                                                                  |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                        | Unique, kebab-case, says the behavior under test                                                                                         |
| `tier`                      | `fast`, `slow` or `network`                                                                                                              |
| `fixture`                   | Folder under `tests/fixtures/`, copied to a temporary directory before the run                                                           |
| `covers`                    | Repository paths this case exercises: `skills/<name>`, `agents/<file>`, `skills/<name>/references/<file>`, `skills/<name>/assets/<file>` |
| `source`                    | The heading in `tests/<skill>.md` this case was derived from                                                                             |
| `prompt`                    | The user message passed to `claude -p`                                                                                                   |
| `tools`                     | The `--allowedTools` string (default `Read,Glob,Grep,Skill`)                                                                             |
| `skills`, `agents`, `reads` | The Skill calls, Agent calls and file reads (regex on the path, or on a Bash command) the transcript must contain                        |
| `must`, `must_not`          | Regexes the final output must and must not match                                                                                         |
| `files`                     | List of `{"glob", "exists", "must", "must_not", "each"}` objects: glob in the working copy (`exists` defaults to true; `each` applies `must` to every matching file instead of all of them together) |
| `no_files`, `unchanged`     | Globs that must match nothing, and files whose hash must not change                                                                      |
| `post`                      | Shell commands run in the working copy that must exit 0; `{repo}` is the repository root                                                 |
| `timeout`                   | Seconds before the run is killed (default 900)                                                                                           |

Assert only what a skill's text requires: a required line, a file written, a file left unchanged, a rules file read. Never assert the whole output, because model output varies. Injection cases give `Write` and `Edit`, so a compromised run could write `pwned.txt` or `owned.txt`; the case fails if it does.

### Adding a case

1. Add or find the section in `tests/<skill>.md` that the behavior comes from.
2. Add the case to `tests/cases/<skill>.json` with a `source` that names that section.
3. Put its input under `tests/fixtures/`. Never put a `spec.md` there: the repository ignores that name.
4. List every skill, agent and rules file it exercises in `covers`. `static` fails when a skill, agent or non-empty rules file is covered by no case.
5. Run `python3 -I tests/run.py static`, then `python3 tests/run.py cases --case <id>`.

## Check-script fixtures

```text
tests/fixtures/
  frontend-react/{base,next}/{clean,seeded}/ + expected.json
  ui-developer/base/{clean,seeded}/          + expected.json
  design-system-builder/{clean/Mini, seeded/MiniLowContrast}/tokens.css
  ui-craft/base/{clean,seeded}/              + expected.json
  visual-qa/{capture,capture-injection,site}/ + fake_cli.py, grades-good.json
  doc-trimmer/  doc-reviewer/  project-planner-pattern/  project-planner-greenfield/
  frontend-react-projects/  ui-developer-projects/  skill-runner/  empty/    (inputs for model cases)
```

`<skill>/<flag-set>/` holds the files for one way of running a check script: `base` is a plain run, and any other name is passed as a flag (`next` runs `--next`). `clean/` files must pass. Each `seeded/` file holds one violation and nothing else the script would fail on, and `expected.json` maps it to a regex its `FAIL` line must match (the same file also holds `clean_files`, the clean file count, and `xfail`, a map of seeded files whose rule is known not to fire yet, which must stay empty).

To add fixtures for a new skill: add `tests/fixtures/<skill>/base/{clean,seeded}/` and `expected.json`, then add the script to `SCRIPT_COVERAGE` in `tests/run.py`. The release checklist's fixtures step picks it up with no change. Keep one `check_*.py` or `audit_*.py` per skill.

## Run logs

`tests/runs/` holds run logs that go in the release notes (`release-process-<version>.md`, `model-cases-<version>.md`). `tests/runs/.cases/` holds raw transcripts and is git-ignored.
