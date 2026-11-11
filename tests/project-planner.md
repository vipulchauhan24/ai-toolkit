# project-planner

## Should trigger

- "Plan this project using docs/spec.md."
- "Phase this spec."
- "Split this into milestones for an agent to build."
- "Break this PRD into phases."
- "Turn this spec into an implementation plan, one phase at a time."
- "Here is my product spec. How should we build it in stages?"
- "Create phase documents for a coding agent from this design."
- "I have an engineering design doc. Cut it into vertical slices."
- "Decompose this spec into agent-ready tasks."
- "Plan the build order for this feature spec."

## Should NOT trigger

- "Poke holes in this spec." (doc-reviewer)
- "Tighten the wording of this spec." (doc-trimmer)
- "Write a spec for a URL shortener."
- "Build the first screen from this phase." (ui-craft or frontend-react)
- "Make me a sprint plan in Linear."
- "Summarise this PRD."
- "What database should I use?"
- "Create a design system."
- "Fix this failing test."
- "Plan my weekend."

## Functional

**Greenfield with files**
- Given: a spec file and "write the phase files"
- When: the skill runs
- Then: it asks about high-stakes gaps (stack, data model, auth) and settles low-stakes gaps as assumptions at the top of the phase. `phases/README.md` holds summaries, a dependency diagram and a parallelization note. Each `phase-N-<slug>.md` stands alone. Phase 1 is a local walking skeleton that pins the stack and `Pattern:`. No document contains TBD.

**Existing codebase**
- Given: a repo and a feature spec
- When: the skill runs
- Then: the stack is inherited, not re-decided, and current-state claims cite `path:line`.

**Inline output**
- Given: a pasted spec and no request for files
- When: the skill runs
- Then: the overview and phase documents are printed inline, separated by `---`, and no file is written.

**Portfolio with fixed colours**
- Given: a portfolio spec in Next.js that fixes three colours, and a run that cannot ask questions
- When: the planner writes phase files
- Then: the first phase is Design direction, done with `design-md` (after `copy-writer`), and passes the colours to `colors.json`; no later phase holds a colour value, a utility class or markup for the look, and each says the look comes from `DESIGN.md`.

**No forward references**
- Given: any generated plan
- When: each phase document is read alone with only the earlier phases done
- Then: it names no interface that a later phase defines.
