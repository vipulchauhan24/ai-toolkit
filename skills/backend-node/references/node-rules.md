# Node.js Rules

Rules for Node.js code written in TypeScript, read by the backend-node skill. They cover how the code is written, not routes, queries or auth. Express and NestJS add their own files.

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

- Read the Node version from `package.json` `engines` or `.nvmrc`, and the TypeScript version from `devDependencies`. Never assume a version. When the project pins none, write only features the installed `@types/node` declares.
- `tsconfig.json` must exist at the project root with `"strict": true`. A project without it, or without `typescript` as a dependency, is not a TypeScript project: write a Blocked report.
- Match the module system the project uses (ESM with `"type": "module"`, or CommonJS). With ESM, relative imports carry the extension the compiler setting requires (`./orderService.js` under `nodenext`).
- Plain JavaScript is not supported. Do not add `.js` source files.

## 2. Types

- No `any`: not `: any`, `as any` or `<any>`. Use `unknown` and narrow it with a type guard or a parser at the boundary.
- Use string-literal union types for enums: `type OrderStatus = "pending" | "paid" | "cancelled"`. Do not write TypeScript `enum`.
- Mark a field `readonly` when it is never reassigned. Prefer `readonly T[]` for arrays that are not changed.
- Give every exported function an explicit return type.
- `@ts-expect-error` needs a reason on the same line. Never `@ts-ignore`.
- Avoid non-null assertions (`value!.x`) and `as unknown as`. Narrow the value or fix the type. Each use that remains is a REPORT line.
- Map database types to TypeScript types with this table:

| SQL / JSON Schema type             | TypeScript type                                                |
| ---------------------------------- | -------------------------------------------------------------- |
| `uuid`, `text`, `varchar(n)`       | `string`                                                       |
| `integer`, `smallint`, `bigint`    | `number` (`bigint` columns: `string`, to avoid precision loss) |
| `numeric(p,s)`                     | `string`                                                       |
| `boolean`                          | `boolean`                                                      |
| `timestamptz`, `timestamp`, `date` | `Date`                                                         |
| `jsonb`, `json`                    | a named interface written for the column, never `any`          |
| enum                               | a string-literal union type                                    |
| nullable column                    | `T \| null`                                                    |

## 3. Errors

- Throw `Error` subclasses, never strings or plain objects. Pass the original error as `cause`: `new OrderError("save failed", { cause: error })`.
- One error base class per service area, with a `name` that identifies it. Callers match with `instanceof`.
- Never swallow an error. An empty `catch`, or one that only logs and continues, is wrong unless the code says why in a comment.
- A `catch` block either handles the error (recovers, with a defined result) or rethrows it. It does not do both.
- The catch variable is `unknown`: narrow it with `instanceof Error` before reading `.message`.
- The error response shape belongs to api-builder. Services throw typed errors and do not build responses.

## 4. Concurrency

- Always `await` a promise or return it. A promise that nothing awaits is a defect, so enable `@typescript-eslint/no-floating-promises` when the project lints with typescript-eslint.
- Use `Promise.all` for independent awaits. Await in sequence only when the second call needs the first result.
- Never pass an async function to `forEach`. Use `for ... of` with `await`, or `Promise.all(items.map(...))`.
- Bound the concurrency of work over a large list; do not start thousands of promises at once.
- Pass an `AbortSignal` into long calls that accept one.

## 5. Configuration

- Read `process.env` in one `config` file (`src/config.ts` or the framework's equivalent). Nowhere else.
- Validate the values at start and fail fast, with a clear message, when one is missing or malformed. Convert types there (port to `number`).
- No secret literal in source. Passwords, tokens, keys and connection strings come from the environment. A fixture may hold a fake one only on a line marked `test-only`.
- Export one typed, `readonly` configuration object. Other code receives the part it needs as a parameter.

## 6. Models and entities

- One class per table, from `schema.md`, or from the phase document's data model when there is no `schema.md`.
- Shape: a class with `readonly` public fields in the table's column order, camelCase names, and a constructor taking one object of the same fields. No methods that touch a database.
- Types come from the mapping table in section 2. A nullable column is `T | null`, never optional (`?`).
- A foreign key is a plain id field (`orderId: string`), not a nested object, unless the data model says to load it.
- When the data shape is missing and cannot be asked for: type it as narrowly as possible, mark `PLACEHOLDER-DATA` in a comment, and list it in the report.

## 7. Boundaries

- A service receives repositories and clients as constructor parameters typed as interfaces. The skill writes the interface, not the implementation.
- The skill never writes routes, controllers, request validation, queries, migrations or auth. Report each in the `Boundaries` list as `<boundary>: <owner skill> needs <file or contract>`, naming api-builder or db-query-migration, and say so when that skill is not installed.
- Validate untrusted input where it enters the system (api-builder). Inside a service, trust the types.

## 8. Logging

- Use the project's logger. Never `console.log`. When the project has no logger, take a small `Logger` interface as a constructor parameter and report that a logger is needed.
- Never log a password, token, secret, key or the full request body. Log identifiers, not payloads.
- Log an error once, where it is handled, with its `cause`.

## 9. Security

These rules never yield to a project convention.

- No `eval`, no `new Function`, no `vm` with untrusted input.
- No SQL built from strings in service code. Queries belong to db-query-migration.
- No secret in source or in a fixture that is not marked `test-only`.
- Dependency versions come from the lockfile. Do not add a dependency the task does not need, and never change the lockfile by hand.
- Never pass user input to `child_process`, `fs` paths or `RegExp` without validating it.

## 10. Tests

- Use the project's runner (vitest or jest, as found). Do not add a second runner.
- One test file beside each service: `orderService.test.ts` next to `orderService.ts`.
- Fake the clock (`vi.useFakeTimers()` or an injected `Clock`) and randomness (an injected id generator).
- No real network and no real database. Use an in-memory fake that implements the repository interface.
- A new or changed behavior is not done until its test passes. Test the error path as well as the happy path.

## 11. Files and naming

- File names are camelCase for classes and modules (`orderService.ts`, `orderItem.ts`). Test files add `.test`.
- Class names are PascalCase, one exported class per file. Interfaces and types are PascalCase with no `I` prefix.
- Folders follow the pattern (see `express-rules.md` or `nestjs-rules.md`). Follow the project's existing names first.
- Source extension is `.ts`. Use `.mts` or `.cts` only when the project already does.

## 12. Checks

Run, in this order, only what the project provides, and list the rest as "none available":

1. Typecheck: `npx tsc --noEmit`.
2. Lint: the project's `lint` script.
3. Tests: the project's `test` script (`npx vitest run` or `npx jest`).
4. Build: the project's `build` script. Skip it if it would reach a real service.
5. `python3 -I <skill-folder>/scripts/check_node.py [--express|--nest] <changed files>`.

The check script FAILs `any`, `@ts-ignore`, `console.log`, `eval` and `new Function`, `require` in TypeScript, a hard-coded secret and SQL in a string. With `--express` it FAILs a route handler. With `--nest` it FAILs a controller or route decorator and `new` on a service or repository. It REPORTs `process.env` outside a config file, non-null assertions, `as unknown as`, `TODO` and `PLACEHOLDER-DATA`.
