# Phase 1: orders services

Approved: 2026-11-05

Pattern: layered
Reason: FastAPI projects default to layered.

## In scope

- An `Order` model in `app/models/order.py` and an `OrderService` in `app/services/order_service.py` with a `get` method.
- The `GET /orders/{id}` route handler.

## Data model

`orders`: `id` uuid primary key, `total_cents` integer not null at least 0.
