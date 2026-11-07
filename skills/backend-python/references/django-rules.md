# Django Rules

Rules for Django code, read by the backend-python skill when the project depends on `django`. Read `python-rules.md` too. Read the Django version from the project and never use features newer than it.

## Contents

1. Layout
2. Models
3. Managers
4. Settings
5. Services
6. Signals
7. Boundaries
8. Tests
9. Files and naming
10. Checks

## 1. Layout

Django defaults to the `mvc` pattern (see `architecture-patterns.md`). Per app:

```text
orders/
  models.py      the model
  services.py    business logic
  tests.py       tests
```

Views and URLs (the controller) belong to api-builder. There is no `selectors.py`: queries are not written here. Keep the project's own app layout if it differs. Read `manage.py` and `settings.py` to find the apps.

## 2. Models

- One model per table. Set the table name with `Meta.db_table`.
- Define `__str__` on every model.
- Field mapping:

| Column type           | Django field                                                               |
| --------------------- | -------------------------------------------------------------------------- |
| `uuid` primary key    | `UUIDField(primary_key=True, default=uuid.uuid4)`                          |
| `text`                | `TextField`                                                                |
| `varchar(n)`          | `CharField(max_length=n)`                                                  |
| `integer`             | `IntegerField` (add `MinValueValidator` for a check constraint)            |
| `numeric`             | `DecimalField(max_digits=p, decimal_places=s)`                             |
| `boolean`             | `BooleanField`                                                             |
| `timestamptz`         | `DateTimeField`                                                            |
| `jsonb`               | `JSONField`                                                                |
| foreign key           | `ForeignKey(..., on_delete=<action from schema.md>)`                       |

- Always write `on_delete` explicitly, using the action in `schema.md` or the phase document. If none is given, ask (interactive) or mark `PLACEHOLDER-DATA` and list it (non-interactive).
- Enums are `models.TextChoices`.
- A nullable column is `null=True`; add `blank=True` only for forms the project already has.

## 3. Managers

Write no custom manager and no custom queryset method. Queries belong to db-query-migration. Use the default `objects` manager only in tests and in service code that saves or deletes one instance.

## 4. Settings

- Settings are driven by the environment.
- `DEBUG` is read from the environment and defaults to False. Never `DEBUG = True`.
- `SECRET_KEY` comes from the environment. Never a string literal.
- Do not change settings the task did not ask about.

## 5. Services

Business logic goes in `services.py`, as plain functions or classes, not in models, and not in views. A service takes plain values or model instances and returns a model instance or a plain value. It never receives a request.

## 6. Signals

Do not add signals. Keep using them only where the project already does.

## 7. Boundaries

- Views, URL routing, serializers and authentication: api-builder. Write no function whose first parameter is `request`, and no `HttpResponse`, `JsonResponse` or `render(`.
- `makemigrations`, `migrate` and migration files: db-query-migration. Never run `makemigrations`. The verify step runs `python manage.py check` and `python manage.py test` only.
- Report each in the `Boundaries` list, for example `migration files: db-query-migration needs schema.md`.

## 8. Tests

- Use `django.test.TestCase`.
- Test the model invariants and each service function.
- The project's test database is used as configured. Fake the clock; no real network.

## 9. Files and naming

- Models are singular `PascalCase` (`Order`); `db_table` is the plural `snake_case` table name from the schema.
- App modules are `models.py`, `services.py`, `tests.py` (or a `tests/` package if the project uses one).

## 10. Checks

Run `python manage.py check`, then `python manage.py test`, then `check_python.py --django` on the changed files. `--django` FAILs on view code, `DEBUG = True` and a string-literal `SECRET_KEY`.
