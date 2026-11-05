# Examples

## Example 1: Greenfield spec, files requested

User says: "plan this project using docs/link-shortener-spec.md and write the phase files"

Actions:
1. Read the spec. No codebase exists, so this is greenfield: Phase 1 must pin the stack and the coding pattern once, each with a rationale.
2. The spec leaves the database open. That is high-stakes, so ask, naming the options and a recommendation. Settle a low-stakes gap (default page size) yourself and record it as an assumption at the top of the affected phase.
3. Cut vertical slices, not layers: a local walking skeleton first, then one capability per phase, then a delivery phase shaped to the project type.
4. Write `docs/phases/README.md` (summaries, dependency diagram, sequencing reason, parallelization note) and `docs/phases/phase-N-<slug>.md`. Run the Handoff Readiness Checklist, then the final self-check.

Result: an index plus one self-contained phase document per phase, with no TBDs and every field typed.

## Example 2: Existing codebase

User says: "phase this spec" with a PRD for a feature in a Django project.

Actions: read the codebase first. Inherit the language, framework, database and pattern, and cite `path:line` for every current-state claim. Introduce a new library only with a stated reason. No stack questions, since the stack is already decided.

Result: phases that match the existing conventions, printed inline unless the user asked for files.
