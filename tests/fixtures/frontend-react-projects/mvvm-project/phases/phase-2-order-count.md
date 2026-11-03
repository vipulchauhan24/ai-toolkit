# Phase 2: Order count badge

## Decisions and assumptions

- Brownfield. Stack is inherited: React 19, TypeScript, Vite.
- Pattern: mvc
- Reason: the team prefers controllers for request handling.

## Product

### Phase goal

Show the number of orders above the order list.

### In scope

- A component `OrderCount` that shows the number of orders returned by the existing `fetchOrders`.

### Acceptance criteria

1. `OrderCount` renders "N orders" for N orders.

## Engineering

### Components touched

`src/features/orders/OrderCount.tsx` (new).
