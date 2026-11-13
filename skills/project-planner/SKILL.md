---
name: project-planner
description: >
  Splits a product + engineering spec into phases, each a working vertical slice with its own agent-ready design doc, plus an overview with dependency order. Asks about high-stakes decisions (stack, data model, auth) before writing. Use for "plan this project", "phase this spec", "split this into milestones for an agent to build", "break this spec into phases", "turn this PRD into an implementation plan", or when the user shares a spec or PRD and wants it built in stages. Works for new projects and existing codebases. Not for reviewing or critiquing a spec (use doc-reviewer), not for tightening its wording (use doc-trimmer), and not for building the UI or code itself (use ui-craft or frontend-react).
license: MIT
compatibility: Reads a spec file and, for an existing project, its codebase. Writing phase files needs file access.
model: opus
---

# Phased Spec Decomposition

Take one product + engineering spec and turn it into an ordered sequence of phases, each with its own standalone design document, to hand to a coding agent one phase at a time. Every document must be implementable on its own, with no unresolved questions.

**North star:** every phase document leaves zero design decisions for the implementer. An agent cannot make a different reasonable choice than the one the document specifies, because every choice is already made and written down.

## Input

If the user has no spec yet, point them to `assets/spec-template.md` in this skill's folder.

Accept a PRD, an engineering design doc, a combined spec, or rough notes that mix product intent with technical detail. If the input only covers product intent, infer a reasonable engineering approach and mark it as an assumption. If it only covers engineering, infer the product framing (who benefits, what they can now do) for each phase.

## Verify Before Writing

Read a `.pdf` with the Read tool, which extracts its text (use its `pages` option for a long file). Use `pdftotext` only if the Read tool cannot open it. Never install a package (pip, npm, apt or any other) to read a document: if nothing can read it, ask for the text.

If a codebase is available, read it before writing any engineering content. Cite what exists today with `path:line`, not from memory or from what the spec assumes. If no codebase exists yet (greenfield), say so explicitly and proceed on the spec alone.

For each phase, note **what already exists** that the phase can reuse -- an existing service, table, endpoint, or library that solves part of the problem. Never let a phase rebuild something the codebase already has.

## Standing Project Rules

Before writing any phase document, read `references/project-planner-rules.md`. It holds the rules you follow when writing phase documents: how to turn the user's engineering preferences (stack, errors, validation and security, tests, migrations, code conventions, git, docs) into concrete decisions inside each phase, plus a fixed block of working rules to embed at the top of every phase document. The implementing agent sees only the phase document, so write each applicable rule as a concrete value in the document; do not reference the rule by name.

- **Precedence:** the existing codebase's conventions win over these rules, and an explicit rule in the source spec wins over them. Note any such difference at the top of the affected phase document.
- **Exceptions:** if a phase must break a rule, name the rule and the reason in that phase's document. Never break one silently.
- **If the file is missing:** say so in one line and continue with sensible defaults; do not stop.

## Tech Stack Choices

**Brownfield (existing codebase):** the stack is not a decision to make -- it's whatever Verify Before Writing found. Match the existing language, framework, database, and libraries. Introducing a new one requires a stated reason (the existing stack cannot do what this phase needs), never preference or unfamiliarity with what's there. Record the codebase's own coding pattern in Phase 1, read as `references/architecture-patterns.md` describes, as a `Pattern: <mvc|mvvm|layered>` line followed by a `Reason:` line that cites the files showing it with `path:line`. Do not choose one from that file's table. If the spec names a different pattern, that is a high-stakes ambiguity: ask the user.

**Greenfield (no codebase yet):** Phase 1's document must pin the full stack once -- language, framework, database, hosting/deploy target, coding pattern, and any non-trivial third-party library -- each with a one-line rationale. Choose the coding pattern from `references/architecture-patterns.md`: use the spec's pattern if it is marked `fixed`, otherwise the default for the pinned framework. Write it as `Pattern: <mvc|mvvm|layered>` followed by `Reason: <one line>`. Every later phase inherits this as a given; never re-open the stack in a later phase's document.

**Default to boring.** Prefer established, widely-used technology over novel tools unless the spec states a hard requirement only the novel choice satisfies -- name that requirement when it justifies the departure.

**A stack change mid-project is a decision, not a detail.** If a later phase needs a new language, datastore, or framework the earlier phases didn't use, call it out as its own decision in that phase's document: the reason, the alternative considered, and the migration cost to anything already built in the old stack.

## Core Principle: Vertical Slices, Not Layers

Never phase by layer ("schema, then API, then UI" or "backend, then frontend"). A layer-based phase produces nothing a user or downstream system can exercise until every layer is done. Instead, cut vertically: each phase touches every layer it needs -- however thinly -- and ends with something that runs end to end and demonstrates real behavior.

Phase 1 is a local walking skeleton: the thinnest possible path through the full system for one trivial flow (for example, save a record and read it back), wired for real (real network calls, real storage, real auth if auth gates the flow), not stubbed. The most important real scenario from the spec lands in the phase after the skeleton, not in Phase 1. Every phase after that adds one more increment of capability on top of a system that already works.

**Example -- a URL shortener spec.**

Bad (layer-based -- nothing works until phase 3):

- Phase 1: database schema for `urls` and `clicks`.
- Phase 2: REST API for create/redirect/stats.
- Phase 3: frontend page to create and view links.

Good (vertical slices -- each phase is a working product):

- Phase 1: local skeleton -- a form saves a long URL to the real database and shows it back, started with one command. No short codes, no auth yet.
- Phase 2: paste a long URL, get a short code back, visiting the short code redirects to the long URL. No auth, no stats yet.
- Phase 3: short codes are scoped to a logged-in user's account (adds auth end to end: login, ownership check, per-user list view).
- Phase 4: click count and last-accessed time shown on each link (adds the `clicks` table, an increment-on-redirect write, and a stats row in the UI).

Deployment is not a phase: the user deploys (Rule 10).

## Sequencing Rules

1. **Phase 1 is a local working skeleton.** It should touch every architectural component the final system needs, at minimal depth, for one trivial flow, and run locally with one command. It holds no deployment or release work (see Rule 10).
2. **Each phase adds exactly one coherent capability.** If a phase description needs "and" to summarize it in one sentence, it is probably two phases.
3. **Order by dependency, not by convenience.** A phase may only depend on capabilities delivered in strictly earlier phases -- never on a phase that comes after it. When dependency order leaves a tie, do the riskiest or least-certain part first -- incremental and reversible beats big-bang; surface unknowns while there is still time to change course.
4. **Every phase ends in a working, demoable state.** Stopping after any phase should never leave the system half-built or non-functional.
5. **Fold plumbing into the phase that needs it.** Do not create a phase whose sole content is infrastructure, schema, or scaffolding with no observable behavior -- attach that work to the first phase that exercises it.
6. **Name cross-cutting concerns explicitly.** For auth, observability, validation, rate limiting, and error handling, state per phase whether a minimal version is enough or the full version is required, and call out which later phase upgrades it.
7. **Let complexity set the phase count.** Do not force a round number of phases. Count independent capabilities, integration points, and risk areas in the source spec; that count drives the number of phases.
8. **Bound each phase's size.** A phase should be implementable in roughly 1-3 focused agent sessions and land as one PR. If a phase touches more than ~8 files or introduces more than 2 new services/classes, split it further. Setup and boilerplate files (configs, lockfiles, CI definitions, generated code) do not count toward the file limit; only files with behavior do. If even the skeleton is too large under this count, split it again into smaller working slices -- never by layer.
9. **Don't design what already exists.** Before specifying a new pattern, queue, cache, or abstraction inside a phase, check whether the stack already has a built-in or established pattern for it.
10. **No delivery phase and no testing phase.** The user deploys and releases by hand. Never write a phase for deployment, hosting, CI/CD, publishing to a registry, or a release, and say so in one line in the overview: "Deployment and release are not planned; you do them." Never write a phase whose only job is testing (end-to-end, browser or visual testing): each phase carries its own test plan, and visual checks of the UI are run separately. For a published project (library, SDK, CLI, plugin), the public API surface (names, signatures, types, errors) takes the place of "API contracts," usage examples take the place of the "UX flow," and every phase that changes the public API states the version bump (major, minor, patch) and any breaking change in its Rollout section.

11. **The look belongs to `design-md`.** Read the page kind from the spec's `Page kind` line (ask if a project with pages leaves it out). For a portfolio or personal site, the first phase is **Design direction**: `ai-toolkit:copy-writer` writes `COPY.md`, then `ai-toolkit:design-md` proposes three concepts the user chooses from, and writes `DESIGN.md`, `design.json` and `design.css` at the project root. That phase is done in the user's conversation, because the user chooses. Its acceptance criteria are `COPY.md` approved by the user (Gate C, which the orchestrator runs before `design-md` starts), then those files existing and the user approving the concept. Look decisions in the spec (colours, fonts, a style) are inputs to that phase, listed in it: the user's colours go to `colors.json`, as `design-md` describes, and are not written anywhere else. For any other page kind, the first phase is **Copy**: `copy-writer` writes `COPY.md`, the user approves it (Gate C), and nothing else. The look follows the design system the spec names, and later phases are built by `frontend-react`.
12. **Phase documents never set the look.** After a Design direction phase, never write colour values, font names, spacing or size numbers, Tailwind or CSS classes, or markup for appearance. Name each section the phase adds, where its words come from (`COPY.md`), its behaviour and its accessibility (keyboard, focus, labels, reduced motion), and write `Look: from DESIGN.md`. A section that `DESIGN.md` does not list is named, and `ui-craft` chooses its variant. Every phase that adds a page or section lists the `COPY.md` entries it uses under `Copy used:`. If an entry does not exist yet, the phase says `Copy missing: <page or section>` so the orchestrator runs `copy-writer` before the phase starts.

## Per-Phase Design Document

A reader with zero context on the other phases must be able to implement this one from this document alone.

### Product Section

- **Phase goal** -- one sentence: what this phase unlocks that did not exist before.
- **User story / job-to-be-done** -- who benefits and what they can now do.
- **In scope** -- an exhaustive list of behavior this phase delivers.
- **Out of scope** -- what looks related but is explicitly deferred, and to which later phase.
- **Acceptance criteria** -- numbered, binary, testable statements with real numbers where relevant. "Returns 409 when the slug already exists" and "list endpoint responds in under 200ms for 10k rows" pass; "handles conflicts well" and "is performant" do not.
- **UX flow** -- for user-facing phases, describe the flow step by step (screens, states, transitions) even without visual mockups. Describe what happens, not how it looks: the look comes from `DESIGN.md` (rule 12).

### Engineering Section

- **What already exists** -- code, services, or libraries this phase reuses rather than rebuilds (see Verify Before Writing).
- **Components touched** -- every service, module, or repo this phase creates or modifies.
- **Data model** -- schemas, fields, types, constraints, and migrations, written out in full (as a table or code block), not summarized.
- **API contracts** -- every endpoint or interface added or changed: method, path, request shape, response shape, status/error codes. Use a table or code block per endpoint.
- **Key flows** -- the sequence of operations for the happy path and for each major edge case (empty input, conflict, timeout, partial failure, retry).
- **Dependencies on prior phases** -- the exact interfaces this phase consumes from earlier phases; nothing implicit.
- **Manual prerequisites** -- every step a human must finish before an agent starts this phase, because an agent cannot do it: creating accounts, obtaining API keys, setting secrets in the hosting environment, configuring DNS or domains, enabling billing, app-store or OAuth app registration, approvals. For each step, state what to do, where the result goes (for example, the exact environment variable name and where it is set), and how to verify it is done (a command or check that succeeds). Write "None" if there are none; never omit the entry.
- **Non-functional requirements** -- only the ones this phase must satisfy (latency budget, concurrency, idempotency), stated as numbers or concrete rules, not adjectives.
- **File reference table** -- every file this phase touches, with the change, as a table (`path:line` when referencing existing logic):

  | File                 | Change                         |
  | -------------------- | ------------------------------ |
  | `path/to/file.ts:42` | Add null check before dispatch |

- **Failure modes** -- for each new or changed codepath, name one realistic way it fails in production (timeout, nil reference, race, stale data) and state whether a test covers it, whether error handling exists, and whether the failure is visible to the caller or silent. Flag any silent, untested, unhandled failure as a gap to close before the phase is done.
- **Test plan** -- as a table across the testing pyramid:

  | Layer       | What                        | Count |
  | ----------- | --------------------------- | ----- |
  | Unit        | `service.method()` behavior | +N    |
  | Integration | cross-component flow        | +N    |
  | E2E         | user-visible journey        | +N    |

- **Rollout** -- feature flags, migration order, backward-compatibility requirements. If the phase touches data, infrastructure, or shared state, state the rollback plan -- even "revert the PR" counts, but say it.
- **Definition of done** -- a checklist that maps one-to-one to the acceptance criteria above.

## Resolving Ambiguity

The source spec will have gaps. Never write "TBD," "decide later," or "up to implementer." Sort each gap by stakes before closing it.

**Low-stakes or reversible** (a default page size, a naming convention, a field's exact wording, which existing utility to call) -- make the most reasonable decision yourself, state it as an explicit assumption at the top of the affected phase document, and move on.

**High-stakes or hard-to-reverse** (tech stack, data model shape that other phases build on, auth/security posture, a breaking API change, anything touching money or irreversible data loss) -- do not silently assume. Stop and ask the user before writing the affected phase document. A wrong silent guess here doesn't cost one phase, it compounds through every phase built on top of it. Name the decision, the options, and your recommendation in one short question.

Where a number is missing (a latency budget, a row count, a concurrency limit) and cannot be derived or safely assumed, say so and state how to measure it -- never leave it as a vague adjective.

## Output Structure

1. **Overview** -- one paragraph per phase (goal + what it unlocks), followed by an ASCII dependency diagram across phases plus a one-paragraph sequencing rationale explaining what would break if the order changed.
2. **Parallelization note** -- if two or more phases (or workstreams within a phase) touch disjoint modules and share no dependency, call this out as an opportunity to hand them to separate agents in parallel; group into lanes (`Lane A: phase 2 -> phase 4 (sequential)`, `Lane B: phase 3 (independent)`). Each lane runs in its own git worktree and lands as its own pushed branch. If everything is strictly sequential, say so in one line instead of forcing a diagram.

   Lanes may run in parallel only if the plan settles file conflicts in advance, so state all three of these in the note:

   - **Shared files, by name.** List every file that more than one lane would edit (route tables, config, dependency manifests, migrations, index or barrel files). If a lane would need to edit a shared file in a way that can't be settled up front, do not run those lanes in parallel.
   - **Who changes each shared file.** Assign each shared file to one earlier phase (or to the skeleton), which makes the change before any lane starts, for example by adding the route or config entries that the lanes will fill in. The lanes then only add to separate files.
   - **Merge order.** State which lane's branch merges first, and require the other lanes to update from the main branch before merging. Pick the order by risk and size: the lane that changes more shared behavior goes first.

3. **One fully expanded design document per phase**, in phase order, each self-contained per the template above.

### Where to Write Output

Default to printing the overview and all phase documents inline in the response, separated by a horizontal rule (`---`), unless the user asks for files on disk.

When the user asks for files (or the input itself was a file path), write them to `.plans/phases/` at the root of the project being planned: the git repository's root, or the current working directory when there is no repository yet. Phase documents stay out of the codebase and are never committed.

- Write each phase to `.plans/phases/phase-N-<slug>.md`.
- Always write an index file, `.plans/phases/README.md`, containing the Overview section (phase summaries, dependency diagram, parallelization note) with links to each `phase-N-<slug>.md`.
- Before writing, check that the project's `.gitignore` lists `.plans/`. If it does not, add the line (create `.gitignore` if there is none) and say so in the reply.
- If the user names a different folder, write there instead, and still add that folder to `.gitignore` unless the user says to commit it.

Follow `references/markdown-rules.md` for all Markdown in the output.

## Troubleshooting

| Problem | Cause | What to do |
|---|---|---|
| The spec has gaps in stack, data model or auth | The input leaves a high-stakes decision open | Ask before writing the affected phase. Mark the rest as assumptions with a default |
| The spec is a rough note, not a spec | No template structure | Plan from it if it is clear enough, otherwise suggest `spec-writer` first |
| The codebase cannot be read | Greenfield, or no access | Say so and plan from the spec alone. Cite `path:line` only for code you read |
| A PDF cannot be read | The Read tool cannot open it | Try `pdftotext`. Never install a package. If nothing reads it, ask for the text |

## Examples

See `references/examples.md` for typical runs, including a blocked one where it applies.

## Handoff Readiness Checklist

Before returning the result, verify for every phase document:

- No "TBD," "later," or unresolved open question remains.
- Every high-stakes ambiguity (stack, shared data model, auth posture, breaking changes) was resolved by asking the user, not by silent guess.
- The tech stack is either inherited from the existing codebase or pinned explicitly in phase 1 with a rationale -- never implicit, never re-decided per phase.
- The coding pattern is either inherited from the codebase (with a `path:line` citation) or pinned once in phase 1 as `Pattern:` and `Reason:` lines, and no later phase changes it.
- Current-state claims are backed by `path:line`, not assumed from the spec.
- Every data field and API shape has a concrete type, not just a name.
- Acceptance criteria are testable by inspection or automated test, not by judgment call, and use real numbers wherever a number applies.
- Every failure mode identified has a stated test-coverage and error-handling status.
- A rollback plan is stated for any phase touching data, infra, or shared state.
- The phase depends only on interfaces defined in earlier phases -- check for forward references.
- Every manual prerequisite has a name, a destination, and a way to verify it, or the phase states "None."
- The phase's file count and new-component count fall within the sizing bound, or the oversized phase has been split.
- No phase is a deployment, release, CI/CD or testing-only phase (Rule 10).

**Final self-check.** For each phase document, switch perspective: read it as the implementing agent would, with zero other context beyond the completed prior phases. Try to name one design decision you would still have to make. If you can name one, the document is not done -- go back and decide it.
