# Route file

`.orchestrator/route.json` is the plan in a form the engine can check. You write it from `phases/README.md` and the phase documents. The engine never reads those documents' prose.

## Fields

Top level:

| Field | Meaning |
|---|---|
| `version` | Always `1`. |
| `project` | The project name. |
| `spec` | Path of the approved spec (`spec.approved.md`), relative to the project root. Its hash is recorded at Gate A. |
| `max_parallel` | Helpers running at once. Default `3`. |
| `phases` | The list of phases, in plan order. |

Each phase:

| Field | Meaning |
|---|---|
| `id` | Lowercase letters, digits, `-` or `_`. Use `p<N>` for phase N. |
| `title` | The phase title. |
| `doc` | Path of the phase document, relative to the project root. It must exist. |
| `depends_on` | Ids of the phases that must be merged first. |
| `lane` | Optional label from the plan's parallelization note. Shown only. |
| `files` | Every file the phase changes, as a path, or a directory ending in `/`. No `*`, `{}` or `?`. |
| `skills` | Full skill names, in the order they run, for example `["ai-toolkit:backend-node"]`. Not for parked phases. |
| `model` | The model for the helper, for example `sonnet`. Not for parked phases. |
| `isolation` | `required` when the phase changes code (it runs in a git worktree), else `not required`. Not for parked phases. |
| `parked` | `true` when only the user can do the phase. |
| `park_reason` | Required when parked: what the user must do. |
| `main_session_skill` | Optional, parked phases only: a skill to run in this conversation with the user instead of a helper. |

## Example

```json
{
  "version": 1,
  "project": "sample-plugin",
  "spec": "spec.approved.md",
  "max_parallel": 2,
  "phases": [
    {"id": "p1", "title": "Walking skeleton", "doc": "phases/phase-1.md", "depends_on": [],
     "files": ["src/app.ts"], "skills": ["ai-toolkit:frontend-react"], "model": "sonnet", "isolation": "required"},
    {"id": "p2", "title": "Launch", "doc": "phases/phase-2.md", "depends_on": ["p1"],
     "files": [], "parked": true, "park_reason": "Needs your domain name and DNS access"}
  ]
}
```

## Reading the plan

| Field | Where it comes from |
|---|---|
| `depends_on` | The plan README's dependency block, checked against each phase document's "Dependencies on prior phases". If they disagree, ask the user. |
| `files` | The phase document's "File reference table". Turn a pattern such as `tests/fixtures/x/{clean,seeded}/*` into its directory, `tests/fixtures/x/`. |
| `lane` | The plan README's parallelization note. |
| `parked`, `park_reason` | The routing rules in `routing.md`. |
| `max_parallel` | The worker cap from the start inputs. |

Two phases that can run together (neither depends on the other, directly or through others) must not share a file. When the plan's tables say they do, the plan is wrong: tell the user, and either add a dependency between them or move the file to one phase. Never remove a file from `files` to make validation pass.

## What the engine checks

`validate` prints a FAIL line for each of: a bad or duplicate id, a missing field, a dependency on a phase that does not exist or on itself, a dependency cycle, a missing phase document, a pattern in `files`, a parked phase with no reason, and two phases that can run together but change the same file. A phase with `isolation: required` and no files prints a WARN, because its clashes cannot be checked.
