# <<TITLE>> Rules

Rules for <<LANG>> code, read by the <<NAME>> skill. They cover how the code is written. Replace each stub below with rules, then delete this line.

## Contents

1. Project and versions
2. Types
3. Errors
4. Concurrency
5. Configuration
6. Models and entities
7. Boundaries
8. Logging
9. Security
10. Tests
11. Files and naming
12. Checks

## 1. Project and versions

- Where the version and dependencies are read (`<<PROJECT_FILE>>`), and what to do when the project pins nothing.

## 2. Types

- How values are typed, and what is never allowed.

## 3. Errors

- One error shape, how errors are raised, wrapped and handled.

## 4. Concurrency

- Shared state, async code, cancellation and limits.

## 5. Configuration

- Where settings come from, defaults, and secrets.

## 6. Models and entities

- How entity and model classes are written from `schema.md` or the phase document's data model.

## 7. Boundaries

- The typed boundary to code this skill does not write (handlers, queries, migrations, auth), and input validation.

## 8. Logging

- What is logged, at which level, and what is never logged.

## 9. Security

- Rules that never yield to a project convention.

## 10. Tests

- What gets a test, where tests live, and how they are named.

## 11. Files and naming

- Folder layout and names, following the project's pattern.

## 12. Checks

- The commands the skill runs, and what `scripts/check_LANG.py` FAILs and REPORTs. Run it as `python3 -I scripts/check_LANG.py [framework flag] FILE...`.
