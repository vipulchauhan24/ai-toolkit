# FastAPI Rules

Rules for FastAPI code, read by the backend-python skill when the project depends on `fastapi`. Read `python-rules.md` too. Read the FastAPI version from the project.

## Contents

1. App factory and lifespan
2. Layout for layered
3. Services
4. Settings
5. Async
6. Models
7. Boundaries
8. Tests
9. Files and naming
10. Checks

## 1. App factory and lifespan

- Build the app in a `create_app()` function in `app/main.py`. Do not create the app at import time in other modules.
- Startup and shutdown work goes in a lifespan function passed as `FastAPI(lifespan=...)`, not in `on_event` handlers.
- Registering routers on the app is api-builder's work; leave a typed place for it.

## 2. Layout for layered

FastAPI defaults to the `layered` pattern (see `architecture-patterns.md`):

```text
app/
  main.py        create_app() and lifespan
  config.py      settings
  models/        model classes
  services/      business logic
```

Handlers (routers) and request and response schemas belong to api-builder, and data access belongs to db-query-migration. Keep the project's own layout if it differs.

## 3. Services

- A service is a plain class that takes its dependencies in `__init__`.
- A service never imports `fastapi` or sees a request or response object.
- `Depends` wiring belongs to api-builder. Write the service so it needs no `Depends`.

## 4. Settings

- Use `pydantic-settings` when it is a dependency, else one module that reads `os.environ`.
- One settings object, created once, in `app/config.py`. Required values fail at startup with the variable name.
- Never put a secret in source.

## 5. Async

- Write `async def` services only when the project's data access is async.
- Never call a blocking function inside `async def`.
- Do not mix sync and async data access in one service.

## 6. Models

- When `sqlalchemy` is a dependency, write SQLAlchemy 2.0 declarative classes with `Mapped[...]` and `mapped_column`. Set `__tablename__` from the schema. Write foreign keys with their delete action.
- Otherwise write frozen dataclasses.
- Map column types with the table in `python-rules.md` section 2.
- Pydantic request and response models are not written here; they are api-builder's.

## 7. Boundaries

- Routers, route handlers (`@app.get`, `@router.post` and the others), request and response schemas, error shape and authentication: api-builder.
- Queries, raw SQL and migration files (including Alembic): db-query-migration.
- Report each in the `Boundaries` list, for example `order routes: api-builder needs the services and the endpoint contract`.

## 8. Tests

- Use pytest.
- Fake the clock; no real network.
- Test services directly, with fake dependencies passed to `__init__`. Do not test through HTTP.

## 9. Files and naming

- Modules are `snake_case`; one model per table; services are named `<Thing>Service`.
- Test files are `test_<module>.py` next to the project's test folder.

## 10. Checks

Run the project's type checker, linter and `pytest`, then `check_python.py --fastapi` on the changed files. `--fastapi` FAILs on `@app.` or `@router.` route decorators.
