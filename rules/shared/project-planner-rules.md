---
name: project-planner-rules
description: >
  Rules the project-planner skill follows when writing phase documents. They turn standing engineering preferences into concrete content inside each phase document, so the implementing agent never has to guess. Read this file before writing phase documents. These are starter defaults; edit them to match your own preferences.
---

# Phase Document Rules

These rules apply to the planner, not to the implementing agent. The implementing agent reads one phase document and nothing else, so a preference only counts once the phase document states it as a concrete decision. A rule such as "validate input at the boundary" is not met by quoting it. It is met by naming the boundary, the checks, and the error returned.

The sequencing, sizing, and document-structure rules live in the planner's `SKILL.md`. This file covers the engineering content those documents must carry.

## Turning Preferences Into Decisions

- State every engineering choice as a decision with a value: a name, a number, a status code, a file path. Do not write adjectives such as "fast", "secure", "small", or "robust".
- When a phase depends on a preference below, write the concrete form in the phase document. Do not write "follow the project rules".
- Never delegate a choice to the implementer with words such as "appropriate", "suitable", "as needed", or "where reasonable".
- When a number is missing, write how to measure it and the default to use until it is measured.

## Stack and Dependencies

- Pin the stack in Phase 1 once, with a one-line reason per item. Later phases inherit it and never reopen it.
- Name each new third-party library in the phase that first needs it, with the reason the code cannot be written in-house in a reasonable time. Cryptography, date handling, and parsing standard formats are the usual valid reasons.
- State the exact package name and the version or version range for every new dependency.
- Require a lockfile in Phase 1 and list it in the file reference table.
- Do not add a dependency to a phase for a feature a later phase delivers.

## Errors

- Phase 1 defines the project's single error shape (fields, types, and one example) when the project has any caller-facing errors. Every later phase uses it and names it in its API contracts.
- If the project has no caller-facing errors in Phase 1, define the shape in the first phase that adds one, and say so in the overview.
- Give each error case in a phase its own row: the trigger, the status or code, the message to the caller, and what is logged.
- State what the caller never sees (stack traces, SQL, file paths, internal IDs) for every endpoint or interface that returns errors.

## Validation and Security

- For each phase that accepts input, name the boundary (endpoint, CLI argument, queue message, file upload) and list each field with its type, limits, and the error returned on failure.
- For each protected action, state who may perform it, where the check runs on the server, and the response when the check fails.
- List every secret the phase introduces: its environment variable name, where it is set, and how to rotate it. Put the setup in Manual prerequisites.
- State what the phase logs and what it must not log (secrets, passwords, tokens, personal data). Name the personal data fields the phase stores, if any.
- Name the password hashing algorithm and its parameters in the phase that introduces passwords.
- Name the query access method in the phase that introduces the database, and require parameterized queries in it.
- Treat the items above as floors. A codebase convention or a spec instruction that conflicts with one of them is a high-stakes ambiguity: stop and ask the user, per Resolving Ambiguity.

## Tests

- The test plan lists tests by name or by behavior, not only by count. Each acceptance criterion maps to at least one named test.
- Write each bug-fix phase's first test as the reproduction of the bug, and put it first in the test plan.
- State which layers run offline and what is faked in each layer (clock, network, randomness). State which layers need a real database or service and how the test run gets one.
- State the command that runs the full suite, and the check that must pass before the PR merges.
- For each failure mode in the phase, name the test that covers it, or mark it as an uncovered gap.

## Data and Migrations

- Write each schema change as a migration with the full definition. State that it applies to an empty database and to the previous release.
- A breaking change gets split across phases into add, backfill, switch, and remove. Each step is its own phase or its own PR, and each is backward compatible with the previous release. Say which phase holds each step.
- Give every migration a rollback entry: the exact reverse steps, or "not reversible" with the backup to restore from. Mark the remove step as not reversible.
- State how a migration is proven before merge (for example, applied and reversed on a copy of the previous schema in CI).

## Code Conventions

- In a greenfield project, Phase 1 names the formatter, the linter, and the command that runs both, and requires CI to fail on violations.
- In a brownfield project, cite the existing formatter and linter configuration by `path:line` and require the phase to match it.
- Give file and module names for new code in the file reference table, following the naming already used in the project.
- Specify the structure of a new component (its public functions and their signatures) when later phases consume it.
- Do not ask for refactoring, renames, or cleanup outside the phase's scope. List such work in the out-of-scope section with the phase that owns it, or leave it out.

## Git and Pull Requests

- Each phase lands as one PR. A phase that needs more than one PR is too large; split it.
- State the branch name for each phase, following the project's existing pattern.
- State the PR's required checks. Never plan a merge with failing checks.
- Do not list generated files or build output in the file reference table unless the project commits them.

## Documentation

- Each phase lists the documentation it changes in the file reference table: README sections, API docs, and the decision log.
- Phase 1 creates the README with install, run, test, and deploy commands. Later phases update it when they change those commands.
- When a phase makes an architectural decision, the document records it as a decision: the choice, the reason, and the alternative considered. The phase also names the file where the decision is kept.

## Instructions to Embed in Every Phase Document

Put the following block at the top of every phase document, unchanged, under the heading "Working rules for the implementing agent". The implementing agent has no other source for these.

- Read this document and every file it references before changing code.
- If the code does not match what this document describes, stop and report the difference. Do not guess.
- Make no changes outside this phase's scope. Record anything out of scope in the final report instead of fixing it.
- Do not report the work as done until the tests in the test plan pass and each acceptance criterion is checked off.
- If a test cannot pass because this document is wrong, stop and report which statement is wrong. Do not weaken the test.
- Report in one place at the end: what changed, what was left out of scope, and which checks passed.

## Checking These Rules

Before returning the phase documents, check each one against this list:

- Every item above that applies to the phase appears as a concrete value, not a reference.
- The error shape, the stack, and the lockfile each have exactly one defining phase.
- No migration appears without a rollback entry.
- Every endpoint or interface that accepts input has a validation table.
- The working-rules block is present and unchanged.
