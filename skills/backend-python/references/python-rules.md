# Python Rules

Rules for Python code, read by the backend-python skill. They cover how the code is written, not the HTTP layer, queries or migrations.

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

- Read the dependencies from `pyproject.toml` (`dependencies` and optional groups), else `requirements*.txt` at the project root, else `Pipfile`. A project with none of these files is not a Python project. Nested requirements files are not read; say so in the report.
- Read the Python version from `requires-python` in `pyproject.toml`, else from `python3 --version`. Never use syntax newer than that version.
- Every public function has type annotations on its parameters and its return value.
- If the project has a type checker (mypy, pyright), it must pass. Do not add one.

## 2. Types

- Nullable values: `Optional[T]` when `requires-python` is below 3.10, else `T | None`.
- JSON columns and payloads get a named `TypedDict`. Never `dict[str, Any]` or `Dict[str, Any]`.
- Enums derive from `str` and `enum.Enum` (Django: `models.TextChoices`).
- Value objects are frozen dataclasses.
- A `# type: ignore` always names the error code: `# type: ignore[attr-defined]`.

Type mapping from `schema.md` (SQL or JSON Schema type to Python type):

| SQL / JSON Schema type          | Python type                                                               |
| ------------------------------- | ------------------------------------------------------------------------- |
| `uuid`                          | `uuid.UUID`                                                               |
| `text`, `varchar(n)`            | `str`                                                                     |
| `integer`, `smallint`, `bigint` | `int`                                                                     |
| `numeric(p,s)`                  | `decimal.Decimal`                                                         |
| `boolean`                       | `bool`                                                                    |
| `timestamptz`                   | `datetime.datetime`, timezone-aware                                       |
| `date`                          | `datetime.date`                                                           |
| `jsonb`, `json`                 | a named `TypedDict`, never `dict[str, Any]`                               |
| enum                            | a class deriving from `str` and `enum.Enum`; Django: `models.TextChoices` |
| nullable column                 | `Optional[T]` when `requires-python` is below 3.10, else `T \| None`      |

## 3. Errors

- Catch specific exceptions. Never a bare `except:`.
- Never swallow an error: an `except` body that is only `pass` is wrong. Handle it, log it and re-raise, or let it propagate.
- When converting an exception, raise the new one `from err`.
- Define one small exception class per failure the caller must tell apart. Do not return error codes or `None` to mean failure.
- Never use a mutable default argument: default to `None` and create the value inside.

## 4. Concurrency

- Use `async def` only where the project is already async (an async framework or async data access).
- Never call a blocking function (file or network I/O, `time.sleep`) inside `async def`; use the async equivalent or run it in an executor.
- Do not share mutable module-level state between requests or threads.

## 5. Configuration

- Read the environment in one settings module only. Other modules import the settings, never `os.environ`.
- Fail fast: a missing required value raises at startup with the name of the variable.
- Never put a secret in source, in a default value or in a test fixture that looks real.

## 6. Models and entities

- One class per table in `schema.md`, or in the phase document's data model when there is no `schema.md`. Map each column type with the table in section 2.
- A model holds data and invariants. It makes no database call and no network call.
- Business logic lives in a service class, not in the model.
- Mark any type guessed because the data shape is missing with `PLACEHOLDER-DATA`.

## 7. Boundaries

This skill never writes route handlers or views, request and response schemas, queries or raw SQL, migration files, or authentication. At each of those, stop at a typed boundary: a function signature or protocol the other skill fills in.

End the report with a `Boundaries` list, one line each: `<boundary>: <owner skill> needs <file or contract>`. Example: `order views and URLs: api-builder needs the models and the endpoint contract`. Name db-query-migration for queries and migrations, api-builder for the HTTP layer. Say so when that skill is not installed.

## 8. Logging

- Use the `logging` module with `logging.getLogger(__name__)`. Never `print`.
- Never log a password, token, secret or full request body.
- Log at the level that matches: `info` for events, `warning` for recoverable problems, `exception` inside an `except` block.

## 9. Security

These rules never yield to a project convention.

- No `eval` or `exec`.
- No SQL built from strings, and no SQL at all in this skill's code (section 7).
- No secret in source. Read it from configuration.
- Treat input from outside the process as untrusted; validate it at the boundary, not in models.

## 10. Tests

- Use the project's runner: pytest or unittest. Do not add one.
- Every new service method and model invariant has a test.
- Fake the clock; pass it in as a parameter instead of calling `datetime.now()` inside logic.
- No real network. Fake external calls.
- Test functions need no return annotation; public helpers do.

## 11. Files and naming

- Modules and functions are `snake_case`; classes are `PascalCase`; constants are `UPPER_SNAKE_CASE`.
- Follow the pinned pattern's layout from `architecture-patterns.md`.
- One class per file only when the class is large; small related classes share a module.
- Do not use `from x import *`.

## 12. Checks

Run the project's type checker, linter and tests, then:

```bash
python3 -I <skill-folder>/scripts/check_python.py [--django] [--fastapi] FILE...
```

FAIL: bare `except:`, swallowed exception, `print(`, mutable default, `eval(` or `exec(`, star import, hard-coded secret, SQL in code (`.raw(`, `.extra(`, `cursor.execute(`), `# type: ignore` without a code, public function without a return annotation. `--django` adds view code, `DEBUG = True`, `SECRET_KEY` in source. `--fastapi` adds route handlers. REPORT: `os.environ` outside a settings or config module, `global `, `TODO`, `# type: ignore[code]`, `PLACEHOLDER-DATA`. Limits: line-level; multi-line `def` signatures are not checked for return annotations.
