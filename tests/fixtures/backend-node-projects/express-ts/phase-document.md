# Phase 1: Orders service
Approved: 2026-11-05

Pattern: layered
Reason: the owner chose layered for the api part.

Stack: Node.js, TypeScript strict, Express, vitest.

## Data model

| Table         | Column        | Type                                | Constraint            |
| ------------- | ------------- | ----------------------------------- | --------------------- |
| `orders`      | `id`          | `uuid`                              | primary key           |
| `orders`      | `status`      | enum `pending`, `paid`, `cancelled` | not null              |
| `orders`      | `total_cents` | `integer`                           | not null, 0 or more   |
| `orders`      | `created_at`  | `timestamptz`                       | not null              |
| `order_items` | `id`          | `uuid`                              | primary key           |
| `order_items` | `order_id`    | `uuid`                              | foreign key to orders |
| `order_items` | `sku`         | `text`                              | not null              |
| `order_items` | `quantity`    | `integer`                           | not null, 1 or more   |

## Scope

Entity classes for both tables and an `OrderService` with `create(input)`, tested with an in-memory fake repository.
