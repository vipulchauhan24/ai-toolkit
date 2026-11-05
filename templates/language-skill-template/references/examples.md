# Examples

## Example 1: A model class in an existing <<LANG>> project

User says: "write the model classes for the tables in schema.md"

Actions:
1. Preflight: Python 3 and `scripts/check_LANG.py` exist. Read `<<PROJECT_FILE>>` (the <<LANG>> version and dependencies) and the codebase's pattern.
2. Run typecheck, lint and tests once and note what already fails.
3. List the files to create. Write the types and the model classes for each table in `schema.md`, then the tests.
4. Verify: typecheck, lint, tests, build, then `python3 -I scripts/check_LANG.py <changed files>`. Fix every FAIL.

Result: status `done`, the version read from the project, files changed, assumptions, checks run, and the work that belongs to other skills (route handlers, queries) reported as the typed boundary with its owner.

## Example 2: Blocked

User says: "write this in <<LANG>>" in a project that is not <<LANG>>.

Actions: the project is not <<LANG>>, so stop before writing anything.

Result: a Blocked report that says what is blocked, why (`<<PROJECT_FILE>>` is missing and the project uses another language), and what the caller must supply. Nothing else.
