# NestJS Rules

Rules for NestJS services written in TypeScript, read by the backend-node skill together with `node-rules.md`. NestJS with a layered pattern is the default; see `architecture-patterns.md`. When both `@nestjs/core` and `express` are dependencies, NestJS wins, because Nest pulls Express in.

## Contents

1. Modules
2. Providers and dependency injection
3. Entities
4. Configuration
5. Lifecycle
6. Boundaries
7. Tests
8. Files and naming
9. Checks

## 1. Modules

- One module per aggregate (`OrderModule` for orders and their items).
- A module exports only the providers other modules use. Everything else stays private.
- A module imports the modules it needs. No circular imports; if two modules need each other, move the shared part into a third.
- Do not use `@Global()` unless the project already does.

## 2. Providers and dependency injection

- Constructor injection only. Mark providers `@Injectable()`. Do not use property injection.
- A repository is injected through an interface token: `export const ORDER_REPOSITORY = Symbol("ORDER_REPOSITORY")` with `@Inject(ORDER_REPOSITORY) private readonly repository: OrderRepository`. The skill writes the interface and the token, not the implementation.
- Never `new` a service or repository. Let the container provide it. The check script FAILs `new <Name>Service(` and `new <Name>Repository(`.
- Register providers in the module's `providers` array.

## 3. Entities

- Entities are plain classes with `readonly` fields, built as `node-rules.md` section 6 says.
- Add no ORM decorators (`@Entity`, `@Column`) unless the project already uses the ORM. When it does, follow its existing entities.

## 4. Configuration

- Use `ConfigModule` (`@nestjs/config`) with validation at start. Read values through `ConfigService`.
- `process.env` is read only inside the configuration module or file. Nowhere else.

## 5. Lifecycle

- Use `onModuleInit` to prepare a provider and `onModuleDestroy` to release it.
- `main.ts` calls `app.enableShutdownHooks()` so `SIGTERM` runs the destroy hooks.
- Keep `main.ts` to bootstrap only.

## 6. Boundaries

api-builder owns: controllers, route decorators, pipes, guards, interceptors, exception filters and DTO validation. This skill does not write them.

- Report each as `<boundary>: api-builder needs <file or contract>`, for example `POST /orders handler: api-builder needs the OrderService interface`.
- Report persistence as `<name> implementation: db-query-migration needs schema.md`.
- If api-builder or db-query-migration is not installed, say so in the report.

## 7. Tests

- Build the unit under test with `Test.createTestingModule({ providers: [OrderService, { provide: ORDER_REPOSITORY, useValue: fakeRepository }] })`, then `module.get(OrderService)`.
- The fake is an in-memory class that implements the repository interface.
- No real network and no real database. Use the project's runner (jest or vitest).

## 8. Files and naming

- `order.service.ts`, `order.module.ts`, `order.entity.ts`, `order.service.spec.ts` (or `.test.ts` if the project uses it), in `src/order/`.
- Class names: `OrderService`, `OrderModule`, `Order`. Tokens: `ORDER_REPOSITORY`.
- Follow the project's existing names when they differ and are consistent.

## 9. Checks

Run the checks in `node-rules.md` section 12, with the NestJS flag:

```bash
python3 -I <skill-folder>/scripts/check_node.py --nest <changed files>
```

`--nest` FAILs `@Controller(`, `@Get(`, `@Post(`, `@Put(`, `@Patch(`, `@Delete(`, `@All(`: those belong to api-builder. It also FAILs `new <Name>Service(` and `new <Name>Repository(`.
