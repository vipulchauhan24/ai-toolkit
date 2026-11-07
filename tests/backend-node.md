# backend-node

## Should trigger

1. "Build this in Node with Express."
2. "Write a NestJS service for orders."
3. "Write the entity classes for the tables in schema.md in TypeScript."
4. "Add an OrderService with a vitest test and an injected repository."
5. "Review this Node service against the TypeScript rules."
6. "Fix the any types and the console.log calls in this Node project."
7. "Build phase 2 of the plan in Node." (with a phase document pinning Node and Express)
8. "Add a Nest module and provider for payments."
9. "Set up configuration loading for my Express service in one config file."
10. "Write the service layer for this Node API, no routes."

## Should NOT trigger

1. "Build this in Python with FastAPI." (backend-python)
2. "Write a Julia module." (julia)
3. "Build the REST endpoint for POST /orders." (api-builder)
4. "Write the SQL migration for the orders table." (db-query-migration)
5. "Design the database schema for orders." (db-schema-builder)
6. "Build this in React." (frontend-react)
7. "Write a Fastify server." (unsupported framework)
8. "Explain how the Node event loop works."
9. "Add JWT login to my Express app." (api-builder)
10. "Write a plain JavaScript script that renames files."

## Functional

**New service**
- Given: an Express project with TypeScript strict and vitest, and a phase document with a data model
- When: asked for entity classes and an OrderService, non-interactively
- Then: the typecheck and tests were run once before changes. The entity classes follow the type mapping table. The service receives its repository as an interface. Tests exist. `scripts/check_node.py --express` was run on the changed files with no FAIL. The report has a status line, stack, files, assumptions, checks and a `Boundaries` list.

**Boundaries**
- Given: an Express project and a request for a service plus the `POST /orders` handler
- When: run non-interactively
- Then: no route handler, controller, query or migration is written. The report has a `Boundaries` line naming api-builder and one naming db-query-migration, and says so if either is not installed.

**Fastify project**
- Given: a project whose only server dependency is `fastify`
- When: run non-interactively
- Then: a Blocked report that names `fastify`, and no code.

**No tsconfig**
- Given: a project with `package.json` and no `tsconfig.json`
- When: run non-interactively
- Then: a Blocked report naming `tsconfig.json`, and no code.

**Wrong stack**
- Given: a Python project
- When: asked to build Node code
- Then: it stops with a Blocked report and writes no code.

**Missing Python**
- Given: no `python3` on the machine
- When: the skill starts
- Then: it stops with a Blocked report that names `python3`. It does not fall back to searching files by hand.

**Pinned pattern mismatch**
- Given: a phase document pinning `mvc` and a codebase that uses `layered`
- When: run non-interactively
- Then: a Blocked report containing `Pattern mismatch`, and no code.

**Check script behavior**
- Given: the fixtures in `tests/fixtures/backend-node/`
- When: `check_node.py` runs on a `.js` file, with no file, and on a service reading `process.env` outside a config file
- Then: `SKIP` for the `.js` file, exit 2 with the usage text for no file, and a `REPORT` line for `process.env`.
