# Phase 1: orders model layer

Approved: 2026-11-05

Pattern: mvc
Reason: Django projects default to mvc.

## Stack

Python with Django. The project is a Django project named `shop` with an app named `orders`.

## In scope

- The `Order` and `OrderItem` models in `orders/models.py`.
- A test in `orders/tests.py` that creates an order with two items.

## Out of scope

- Views, URLs and serializers (api-builder).
- Migration files (db-query-migration).

## Data model

`orders`:

| Column       | Type        | Constraints            |
| ------------ | ----------- | ---------------------- |
| `id`         | uuid        | primary key            |
| `status`     | enum        | `pending`, `paid`, `cancelled`; not null |
| `total_cents`| integer     | not null, at least 0   |
| `created_at` | timestamptz | not null               |

`order_items`:

| Column     | Type    | Constraints                                       |
| ---------- | ------- | ------------------------------------------------- |
| `id`       | uuid    | primary key                                       |
| `order_id` | uuid    | foreign key to `orders`, delete action CASCADE    |
| `sku`      | text    | not null                                          |
| `quantity` | integer | not null, at least 1                              |

## Acceptance criteria

1. `Order` and `OrderItem` exist with the columns above, `db_table` set to `orders` and `order_items`.
2. `python manage.py check` and `python manage.py test` pass.
