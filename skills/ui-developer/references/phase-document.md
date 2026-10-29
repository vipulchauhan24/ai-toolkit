# Using a project-planner phase document

Section numbers (§) refer to SKILL.md. Read this file in full when the user gives a phase document.

This skill works without one. If the user gives a phase document (a file `phases/phase-N-<slug>.md`, pasted phase text, or the phases index with a phase named), read the whole phase first.

**Check before building:**

1. **Does the phase have UI work?** Delivery, packaging, backend-only and library phases often don't. If there is none, say "no UI in this phase" in the report and stop. Build nothing.
2. **Do the prior phases exist?** Check that what "Dependencies on prior phases" and "What already exists" name is really in the code. If the code doesn't match the phase document, stop and ask. Don't guess.
3. **Is the foundation yours to build?** Look at the file reference table and the plan's parallelization note. Edit shared files (the entry stylesheet, root layout, dependency manifest) only if this phase's table lists them. If an earlier phase owns them and hasn't landed, don't edit them: report that the foundation is missing and stop.

Then use the phase like this:

| Phase section | Used for |
|---|---|
| Phase goal, user story | What the screen is for and who uses it |
| In scope | The exact list of UI to build. **Build nothing else.** |
| Out of scope | UI to leave out, even if it looks like an obvious addition. List what you skipped in the report |
| UX flow | Screens, states and transitions (§5 step 2) |
| Acceptance criteria | The verification checklist (§7). Report each by number; backend ones are "not UI" |
| Data model, API contracts | Field types, validation rules, loading, empty and error states. Type the screen's data boundary from the contracts exactly; don't invent a shape |
| Failure modes | Each one the user can see becomes an error or empty state in the state list (§5 step 2) |
| Test plan | The UI rows are written with the UI (§7 step 1) |
| Rollout | A feature flag the phase names gates the UI through the project's existing flag mechanism. If there is none, ask |
| What already exists, Dependencies on prior phases | Components and screens to reuse. Don't rebuild them. If Phase 1 defined an error shape, render errors from it |
| Tech stack (pinned in Phase 1) | Inherit it. If Phase 1 pins a UI library, use it and say so; don't re-ask |
| File reference table | The files to create or change. **Build only the UI files**; list the backend files you skipped in the report |
| Manual prerequisites | Check they are done. If one is missing, say what is blocked |

**When the phase and the design system disagree:**

| About | Winner |
|---|---|
| Appearance: color, type, spacing, component look | The design system |
| Behavior, flow, scope, copy, data | The phase |
| Tech stack and component library | The phase, unless it breaks the 0% CSS rule. Then it is a hard blocker (§2): ask, or write the Blocked report |

Note every conflict in the report.

Rules:

- **Don't edit the phase document.**
- **Fill low-stakes gaps** (an unspecified empty state, a button label) from the design system's patterns and list them as assumptions. **Ask** if the gap changes the flow or the data.
- Phases are vertical slices: stay inside the phase's slice and don't polish screens that belong to later phases.
- **Build only the UI half of the phase.** Its data model, API contracts and key flows tell you what the screen needs. They are not work for this skill. Wire the screen to them if they already exist, or type the boundary if they don't (Scope).

Without a phase document, derive the screens from the user's request and ask only what blocks you (§2).
