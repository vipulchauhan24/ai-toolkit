# backend-python

## Should trigger

1. "Build this in Django."
2. "Write the Order and OrderItem Django models from the phase document."
3. "Build the order service in FastAPI."
4. "Write this Django model layer."
5. "Add a service class that creates an order, with a test."
6. "Review this Python code against the rules."
7. "Write the SQLAlchemy model classes for the tables in schema.md."
8. "Move the business logic out of this Django model into services.py."
9. "Fix the swallowed exception and the mutable default in this Python module."
10. "Build phase 2 of the plan in Python." (with a phase document pinning Django)

## Should NOT trigger

1. "Build this in Flask." (unsupported framework)
2. "Build this in Node and Express." (backend-node)
3. "Write a Julia function for this." (julia)
4. "Write the Django view and URL for listing orders." (api-builder)
5. "Add a FastAPI route handler and Pydantic schema for orders." (api-builder)
6. "Write the SQL migration for the orders table." (db-query-migration)
7. "Design the Postgres schema for orders." (db-schema-builder)
8. "Build a React component for the orders table." (frontend-react)
9. "Explain how Python decorators work."
10. "Write a bash script that renames files."

## Functional

**New model layer**
- Given: a Django project with an `orders` app and a phase document pinning `Pattern: mvc`
- When: asked for the Order and OrderItem models and a test, non-interactively
- Then: the models use `UUIDField`, `TextChoices`, an explicit `on_delete` and `Meta.db_table`. `python manage.py check` and `python manage.py test` were run. `scripts/check_python.py --django` was run on the changed files with no FAIL. The report has a status line, stack, files, assumptions, checks and a `Boundaries` list naming api-builder (views and URLs) and db-query-migration (migration files).

**Unsupported framework**
- Given: a project whose `requirements.txt` contains only `flask`
- When: asked to build Python service code, non-interactively
- Then: a Blocked report that names Flask as unsupported, and no code.

**Not a Python project**
- Given: a project with no `pyproject.toml`, `requirements*.txt` or `Pipfile`
- When: asked to build Python code, non-interactively
- Then: a Blocked report that names the missing dependency file, and no code.

**Views are a boundary**
- Given: a Django project and a request for models and the list view
- When: run non-interactively
- Then: it writes the models, writes no view and no URL, and the report lists the view boundary for api-builder.

**Pinned pattern mismatch**
- Given: a phase document pinning `mvc` and a FastAPI codebase that uses `layered`
- When: run non-interactively
- Then: a Blocked report containing `Pattern mismatch`, and no code.

**Missing Python**
- Given: no `python3` on the machine
- When: the skill starts
- Then: it stops with a Blocked report that names `python3`. It does not fall back to searching files by hand.
