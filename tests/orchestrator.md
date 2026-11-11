# orchestrator

The engine (`skills/orchestrator/scripts/engine.py`) is tested offline by `python3 -I tests/run.py scripts`: route validation against nine broken routes, then a whole sample project run through every command. The cases below test the skill's own behavior with a model.

## Should trigger

- "Build this project from the spec."
- "Orchestrate this plan."
- "Run the phases in phases/ in order."
- "Take this spec all the way to a built app."
- "Carry on with the next phase."
- "I have a phases folder. Build all of it."
- "Run the whole plan with helpers in parallel where you can."
- "Where are we on the build? Continue it."
- "Start the build from spec.approved.md."
- "Use the orchestrator on this project."

## Should NOT trigger

- "Build this screen." (frontend-react)
- "Write this React component." (frontend-react)
- "Write the Node service for orders." (backend-node)
- "Plan this project using docs/spec.md." (project-planner)
- "Write a spec for this brief." (spec-writer)
- "Poke holes in this plan." (doc-reviewer)
- "Create a design system."
- "Explain what a DAG is."
- "Merge my open pull requests."
- "Schedule a nightly build."

## Functional

**Resume**
- Given: a project whose `.orchestrator/state.json` shows phases 1 and 2 merged and phase 3 parked, and a prompt "carry on" that forbids starting helpers
- When: the skill runs
- Then: it runs the engine's `status` and `next` and does not run `init`. It says 2 of 3 phases are merged and that phase 3 waits for the user, and quotes what the user must do. It starts nothing.

**Route from a plan**
- Given: an approved spec and a `phases/` folder with a README and three phase documents, and an instruction to write the route and stop before Gate B
- When: the skill runs
- Then: it writes `.orchestrator/route.json` with a dependency chain p1, p2, p3, the language skill for phases 1 and 2, and phase 3 parked with its manual steps as the reason. The engine's `validate` ends with `RESULT  PASS`. No `state.json` exists, so no gate was approved and nothing started.

**Nothing to start from**
- Given: an empty folder and the prompt "orchestrate this"
- When: the skill runs
- Then: it asks for a spec, a brief, or the path to a phases folder, and writes no `.orchestrator/` folder.

**Engine refusal is final**
- Given: a route whose Gate B was approved and then edited
- When: the skill asks `next`
- Then: the engine's refusal is reported to the user, and no helper is started.
