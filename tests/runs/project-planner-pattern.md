# Recorded runs: planner pattern pin (phase 1, criteria 7 and 8)

Date: 2026-11-03. Run headless with `claude -p`, the plugin loaded from this repo with `--plugin-dir`, tools limited to Read, Glob, Grep and Skill. Inputs are in `tests/fixtures/project-planner-pattern/`. The full outputs are not stored. The excerpts below are copied from them.

## Run 1: brownfield (criterion 7)

Input: `brownfield-spec.md` with `sample-project/` as the codebase.

A first run named the pattern in the overview with `path:line` citations but wrote no `Pattern:` line, so `grep 'Pattern: layered'` failed. The skill text said only "record the codebase's own coding pattern with a path:line citation". `skills/project-planner/SKILL.md` and `rules/shared/project-planner-rules.md` were changed to require the `Pattern:` and `Reason:` lines in brownfield too. The run below is the rerun after that change.

Excerpt from the Phase 1 document:

```text
### Coding pattern

Pattern: layered

Reason: `src/routes/orders.ts:2` imports only the service, `src/services/orderService.ts:2` imports only the repository, `src/repositories/orderRepository.ts:1` imports only the model, and no file imports upward.
```

Later phases inherit it: `Pattern: layered, inherited from Phase 1. Not reopened.`

Checks:

```text
$ grep -E 'Pattern: layered' output     -> 2 matches (Phase 1 line and the Phase 2 inheritance line)
$ grep -E 'src/[a-zA-Z/]+\.ts:[0-9]+' on the Reason line -> src/routes/orders.ts:2, src/services/orderService.ts:2, src/repositories/orderRepository.ts:1
```

Result: pass.

## Run 2: greenfield (criterion 8)

Input: `greenfield-spec.md`, no codebase, coding pattern line left `planner decides`.

Excerpt from the Phase 1 document (after the stack table):

```text
Pattern: layered

Reason: the spec leaves the pattern to the planner and layered is the FastAPI default in the pattern table.
```

Phase 1 decision log also records: `D1: Pattern: layered. Reason: FastAPI default. Alternative: mvc, rejected because there is no view layer.`

Checks:

```text
$ grep -E 'Pattern: (mvc|mvvm|layered)' output -> 2 matches
$ grep 'Reason:' output                        -> present directly under the Pattern line
```

Result: pass.
