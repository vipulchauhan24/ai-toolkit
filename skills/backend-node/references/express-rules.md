# Express Rules

Rules for Express services written in TypeScript, read by the backend-node skill together with `node-rules.md`. Express with a layered pattern is the default; see `architecture-patterns.md`.

## Contents

1. App factory
2. Layout for layered
3. Services and dependency passing
4. Configuration
5. Shutdown
6. Boundaries
7. Tests
8. Files and naming
9. Checks

## 1. App factory

- `createApp()` in `src/app.ts` builds and returns the Express app. It does not call `listen`.
- `src/server.ts` is the only file that calls `listen`. It reads the port from configuration and starts the app.
- Tests import `createApp()`, never `server.ts`.

## 2. Layout for layered

```text
src/
  app.ts          createApp()
  server.ts       listen, shutdown
  config/         the one place that reads process.env
  models/         entity classes, one per table
  services/       business logic; imports models only
```

- Imports point one way: `services` import `models` and interfaces; `models` import nothing from the project.
- Routes sit in a layer that imports `services`. That layer belongs to api-builder, so this skill does not write it.
- Follow the project's existing folders when they differ from this layout and the project is consistent.

## 3. Services and dependency passing

- A service is a class whose constructor takes its dependencies (repository interfaces, a clock, a logger) as parameters. No module-level singletons, no importing a concrete repository.
- Wire the services in one place, the composition root in `createApp()` or a function it calls.
- A service method takes plain typed input and returns a model or plain data. It never takes or returns `Request` or `Response`.

## 4. Configuration

- One `src/config.ts` (or `src/config/index.ts`) reads `process.env`, validates it at start and exports a typed object.
- `createApp()` receives the configuration it needs as a parameter. It does not read `process.env`.

## 5. Shutdown

- In `server.ts`, handle `SIGTERM` (and `SIGINT`): stop accepting connections with `server.close()`, wait for the callback, release resources, then exit with code 0.
- Add a timer that forces exit with a non-zero code when shutdown takes longer than the configured limit. Call `unref()` on it.

## 6. Boundaries

api-builder owns: route handlers, request parsing, request validation, the error response middleware, authentication and authorization middleware. This skill does not write them.

- Report each as `<boundary>: api-builder needs <file or contract>`, for example `POST /orders handler: api-builder needs the OrderService interface`.
- Report persistence as `<name> implementation: db-query-migration needs schema.md`.
- If api-builder or db-query-migration is not installed, say so in the report.

## 7. Tests

- Test services directly with an in-memory fake of each repository interface. Do not start the server in a service test.
- Test `createApp()` only for wiring that this skill wrote, with no network port (never call `listen`).
- Use the project's runner (vitest or jest).

## 8. Files and naming

- `src/app.ts`, `src/server.ts`, `src/config.ts`.
- `src/models/order.ts`, `src/models/orderItem.ts`: camelCase file, PascalCase class.
- `src/services/orderService.ts` with `src/services/orderService.test.ts` beside it.

## 9. Checks

Run the checks in `node-rules.md` section 12, with the Express flag:

```bash
python3 -I <skill-folder>/scripts/check_node.py --express <changed files>
```

`--express` FAILs `app.` or `router.` followed by `get`, `post`, `put`, `patch`, `delete` or `all` and `(`: a route handler. If the FAIL is a call that is not a route (for example a `Map` named `app`), rename the variable.
