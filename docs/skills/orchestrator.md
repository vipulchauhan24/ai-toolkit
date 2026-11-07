# Orchestrator Skill

The orchestrator takes a spec through to merged pull requests. It gets the spec written and approved, gets the project split into phases, then runs each phase through the right skills in a separate git worktree, in dependency order. It stops at the points where you decide, and it never merges for you.

It works in Claude Code only. It is the one skill that calls other skills: spec-writer, doc-trimmer, doc-reviewer, project-planner and design-system-builder run in your conversation, because they ask you questions. Each build phase runs in the `skill-runner` agent in its own worktree, in the background, because a build does not need to ask anything.

## The conductor and the engine

Two parts share the work.

- The conductor is Claude following `SKILL.md`. It talks to you, asks the questions, starts the helpers and reads what they report.
- The engine is a small Python script, `skills/orchestrator/scripts/engine.py`. It holds the route (which phases exist and what each waits for) and the ledger (what has happened to each). It starts nothing. It only says what may start, and it refuses anything that breaks the route.

The conductor does not decide the order from memory. It asks the engine, and does what the engine says. That is what stops a step from being skipped, a phase from starting early, or a failed phase from being built on.

## What You Need

- Claude Code with the Agent and Skill tools, a git repository, and the `ai-toolkit` plugin installed (the orchestrator starts `ai-toolkit:skill-runner`).
- **Python 3.9 or later** (required). It runs the engine. Without it, the skill stops and says so.
- The `gh` command logged in, if you want the orchestrator to open pull requests.
- A spec, a short brief, or a `phases/` folder from project-planner.

## Using the Skill

In Claude Code, open the project and ask:

- `build this project from the spec`
- `orchestrate the plan in phases/`
- `carry on with the next phase`

It asks once for anything missing: the spec or brief, the project name, the base branch, the design system and how many helpers may run at once (3 by default). Reply `use defaults` to take the defaults.

Add `.orchestrator/` to the project's `.gitignore`. The route, the ledger and the runner reports live there.

### What happens, in order

1. **Spec.** A brief, or a spec with gaps, goes to spec-writer, which asks every gap in one batch and writes `spec.md`. Doc-trimmer and doc-reviewer run on it (always for a spec the skill drafted, on request for yours). You read the three files.
2. **Gate A.** You say which file is approved. It becomes `spec.approved.md`. Nothing later reads any other spec file.
3. **Phases.** If `phases/` exists it is read. Otherwise project-planner writes it and asks you the stack, data and auth questions.
4. **Route.** The orchestrator writes `.orchestrator/route.json` from the plan and the engine validates it: no missing dependency, no cycle, and no two phases that can run together change the same file.
5. **Gate B.** You see one table: each phase, its skills, what it waits for, what runs side by side, and what is parked for you. You confirm or edit.
6. **Build loop.** The engine says which phases may start. The orchestrator starts them in worktrees, up to the helper cap. When one finishes, the engine reads its report and accepts it only if every skill is `done` and shows evidence.
7. **Pull requests.** For each batch you are asked once: commit, push and open a pull request for each? Only on yes.
8. **Merge.** You merge in GitHub and tell the orchestrator. It asks you to update the base branch, marks the phase merged, and the phases that waited for it can start.

### What it parks

A parked phase is one only you can do: buying a domain, setting a secret, launching, or anything the plan marks as a manual step. Phases that need a skill that is not installed (api-builder and the database skills until release 1.7.0) are parked too. Parked phases keep their place in the route and their dependents wait. When you have done the step, say so and the orchestrator marks it merged.

### When a phase fails

The engine marks it failed and halts every phase that depends on it. Independent phases keep going. The orchestrator tells you what failed and asks: retry, fix the phase document, or stop.

### Carrying on later

The ledger is a file, so a new session can resume. Ask `carry on` and the orchestrator reads the ledger, says where things stand and continues. It does not plan again.

## The files

| File | What it holds |
|---|---|
| `.orchestrator/route.json` | The route: phases, dependencies, files, skills, models. See `skills/orchestrator/references/route-format.md`. |
| `.orchestrator/state.json` | The ledger: the status of each phase, the approved spec and route hashes, a log of every command. |
| `.orchestrator/runs/<phase>-<n>/report.md` | The runner's report for one attempt. |

The engine records a hash of the approved spec at Gate A and of the route at Gate B. If either changes afterwards, it refuses to continue until you approve again.

## The engine commands

You do not need these, but they are there to inspect a run. From the project root:

```bash
python3 -I skills/orchestrator/scripts/engine.py status
python3 -I skills/orchestrator/scripts/engine.py next
python3 -I skills/orchestrator/scripts/engine.py validate
```

The others (`init`, `approve`, `start`, `record`, `pr`, `merge`, `fail`, `retry`) change the ledger and are run by the orchestrator. If the ledger is wrong, `retry <phase>` sends a failed, running or built phase back to pending.

## What the Skill Does Not Do

- It does not write code itself. The skills do.
- It does not merge pull requests, and it does not push or open one without your yes.
- It does not build deployment, hosting or release phases. It parks them for you.
- It does not guess a gap in the spec. It asks, or it records the gap as an open question.
- It does not work outside Claude Code.
- It does not yet record token use or grades. The ledger has a `tokens` field for a run; a report that grades the work comes later.
- The engine cannot physically stop Claude from starting a helper it was not told to. The conductor is instructed to do only what the engine returns, and the ledger records everything, so a departure shows up.

## Customizing the Skill

- Edit `skills/orchestrator/references/routing.md` to change which skills a phase gets, the order they run in, or the model.
- Edit `skills/orchestrator/references/route-format.md` if you change the route fields. The engine's checks are in `scripts/engine.py`, and its tests are in `tests/run.py` (the `engine_tests` function) with fixtures in `tests/fixtures/orchestrator/`.

## Installing the Skill

```text
/plugin marketplace add vipulchauhan24/ai-toolkit
/plugin install ai-toolkit@product-development
```

Or copy the `skills/orchestrator/` folder and `agents/skill-runner.md` into your own plugin. The orchestrator does not work without the `skill-runner` agent.
