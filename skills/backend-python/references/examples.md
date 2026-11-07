# Examples

## Example 1: Django model layer

User says: "Write the Order and OrderItem Django models in orders/models.py and a test in orders/tests.py that creates an order with two items." The phase document pins `Pattern: mvc` and a data model for `orders` and `order_items`.

Actions:
1. Preflight: `python3 --version` works and `scripts/check_python.py` exists. Read `python-rules.md`, `architecture-patterns.md` and `django-rules.md` (`django` is in `requirements.txt`).
2. Read the project: Python version, `manage.py`, `settings.py`, the `orders` app. Run `python manage.py check` and `python manage.py test` once and note what already fails.
3. List the files: `orders/models.py`, `orders/tests.py`. Write `Order` and `OrderItem` with `UUIDField` keys, `TextChoices` for status, `ForeignKey(..., on_delete=models.CASCADE)` and `Meta.db_table`, then the test.
4. Verify: `python manage.py check`, `python manage.py test`, then `python3 -I <skill-folder>/scripts/check_python.py --django orders/models.py orders/tests.py`. Fix every FAIL. Typecheck, lint and build: none available.

Result: status `done`, Python and Django versions, files changed, assumptions, checks run, and a `Boundaries` list:
- `order views and URLs: api-builder needs the models and the endpoint contract`
- `migration files: db-query-migration needs schema.md`

## Example 2: Blocked

User says: "write this order service in Python" in a project whose `requirements.txt` contains only `flask`.

Actions: preflight passes. Reading the project shows Flask is the only web framework, which this skill does not support. Stop before writing anything.

Result: a Blocked report that says what is blocked (the service code), why (Flask is unsupported; the skill supports Django and FastAPI), and what the caller must supply (a Django or FastAPI project, or another skill's help). Nothing else.
