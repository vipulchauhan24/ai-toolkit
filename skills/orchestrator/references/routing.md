# Routing a phase to skills

Read each phase document, not its title. A phase can match more than one row. Use only skills that are listed as available in this session. A skill that the plugin documents but that is not installed is "not installed": the phase is parked, with that in the reason.

## Which skills

| The phase contains | Signals in the phase document | Skills, in this order |
|---|---|---|
| Design direction | Writes `COPY.md`, concepts and `DESIGN.md`; the user chooses the look | Park with `main_session_skill` `ai-toolkit:ui-craft` |
| Screens in React or Next.js, on a project with `DESIGN.md` | Says `Look: from DESIGN.md`, or depends on a Design direction phase; page and section files in the file table | `ai-toolkit:ui-craft`, then `ai-toolkit:frontend-react` |
| Screens in plain HTML, CSS and JS, on a project with `DESIGN.md` | As above, with no framework pinned | `ai-toolkit:ui-craft` |
| Screens, components or styling in React or Next.js, with no `DESIGN.md` | UX flow, screenshots or layout references; page and component files in the file table; React or Next.js pinned | `ai-toolkit:frontend-react`, following the design system the spec names or the project's existing styles |
| Screens in another frontend stack | UI files, and a stack that is not React or Next.js | Park: no skill for that stack |
| Server code in Node.js, Python or Julia | Services, entity classes, model structs, data processing; Node.js, Python (Django or FastAPI) or Julia pinned | `ai-toolkit:backend-node`, `ai-toolkit:backend-python` or `ai-toolkit:julia` |
| Route handlers, controllers, auth, request validation | API contracts, endpoints, login, permissions | `ai-toolkit:api-builder` after the language skill; park if not installed |
| Tables, queries, migrations | Schema, indexes, migration files | `ai-toolkit:db-schema-builder` then `ai-toolkit:db-query-migration`; park if not installed |
| A new design system or token set | Asks to create tokens, themes or a palette | Park with `main_session_skill` `ai-toolkit:design-system-builder` |
| Steps only the user can do | A manual prerequisites section with real steps; dashboards, accounts, DNS, secrets | Park |
| Something public or hard to undo | A rollout that launches, turns on indexing, publishes a release, or migrates production data | Park |
| No usable structure | Free-form notes, no file table, no acceptance criteria | Park, and propose a routing at Gate B |
| Only documents or configuration | Docs, README rows, manifests, version bumps | Park unless a skill clearly fits: no skill writes these in this release |

A phase with both server and screen work lists the server skill first and the screen skills after it, so one phase stays one pull request on one branch.

When `ui-craft` builds a phase, tell it in the brief that this is a phase build: it reads the existing `COPY.md` and `DESIGN.md`, builds only the sections the phase names, and never chooses the look again. `frontend-react` follows it, so the code meets the React rules and the project's checks pass.

Release, version and tag phases are parked: the user runs the release checklist.

## Model

Use `sonnet`. Use `opus` only when one of the phase's skills has `model: opus` in its `SKILL.md` front matter.

## Isolation

`required` for every phase that writes code or files in the project. `not required` only for a phase whose skills change nothing, such as a review.

## Parked phases

A parked phase is not a failure and not skipped. It holds its place in the route, its dependents wait for it, and the user finishes it and says so. Give every parked phase a `park_reason` that says what to do and how to tell it is done, copied from the phase document's manual prerequisites where it has them.

## When the signals disagree

If the file table and the prose point at different skills, or two stacks are pinned, do not choose. Park the phase and put the question to the user at Gate B.
