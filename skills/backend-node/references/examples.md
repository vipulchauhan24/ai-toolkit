# Examples

## Example 1: Entity classes and a service in an Express project

User says: "build this in Node with Express" and names the phase document for the orders service.

Actions:
1. Preflight: Python 3 and `scripts/check_node.py` exist. Read `references/node-rules.md`, `references/architecture-patterns.md`, then `references/express-rules.md` because `express` is in `dependencies` and `@nestjs/core` is not.
2. Read `package.json` (Node 20, TypeScript 5, vitest), `tsconfig.json` (`strict: true`) and the phase document (`Pattern: layered`, the data model for `orders` and `order_items`).
3. Run `npx tsc --noEmit` and `npx vitest run` once and note what already fails (nothing).
4. List the files: `src/models/order.ts`, `src/models/orderItem.ts`, `src/services/orderService.ts`, `src/services/orderService.test.ts`. Write the entity classes (`status` as a string-literal union, `totalCents` as `number`, `createdAt` as `Date`), an `OrderRepository` interface, the service that receives it in its constructor, then the test with an in-memory fake.
5. Verify: `npx tsc --noEmit`, `npx vitest run`, then `python3 -I scripts/check_node.py --express <changed files>`. Lint and build: none available.

Result: status `done`, Node and TypeScript versions, framework Express, files changed, assumptions, checks run and not available, and the boundaries:

```text
Boundaries
- POST /orders handler: api-builder needs the OrderService interface
- OrderRepository implementation: db-query-migration needs schema.md
```

If api-builder or db-query-migration is not installed, each line says so.

## Example 2: Blocked

User says: "build this in Node" in a project whose only server dependency is `fastify`.

Actions: preflight passes, `package.json` shows `fastify` and neither `express` nor `@nestjs/core`. Express and NestJS are the only supported frameworks, so stop before writing anything.

Result: a Blocked report that says what is blocked (Node service code), why (`package.json` depends on `fastify`, which this skill does not support), and what the caller must supply (an Express or NestJS project, or another skill). Nothing else. The same report is written for a project with no `package.json` or no `tsconfig.json`, naming the missing file.
