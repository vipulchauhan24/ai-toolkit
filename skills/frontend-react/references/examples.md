# Examples

## Example 1: A component in an existing Next.js project

User says: "build a paginated orders table in Next.js"

Actions:
1. Preflight: Python 3 and `scripts/check_react.py` exist. Read `package.json` (Next.js 15, App Router, TanStack Query, Vitest) and the codebase's pattern (`layered`).
2. Run typecheck, lint and tests once and note what already fails.
3. List the files to create. Write the typed data boundary first, then the Server Component that fetches, a Client Component for paging, then the tests.
4. Verify: typecheck, lint, tests, `next build`, then `python3 -I scripts/check_react.py --next <changed files>`. Fix every FAIL.

Result: status `done`, stack read from the project, files changed, assumptions (for example page size 20), checks run, and any `PLACEHOLDER-DATA` with the source the real data must come from.

## Example 2: Blocked

User says: "write this component in React" in a Vue project.

Actions: the project is not React for the web, so stop before writing anything.

Result: a Blocked report that says what is blocked, why (`package.json` depends on `vue`), and what the caller must supply. Nothing else.
