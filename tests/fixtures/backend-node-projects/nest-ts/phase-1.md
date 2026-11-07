# Phase 1: Orders service

Pattern: layered
Reason: the owner chose layered.

Stack: Node.js, TypeScript strict, NestJS, vitest.

Write an `Order` entity (`id` uuid, `status` enum pending, paid, cancelled, `total_cents` integer, `created_at` timestamptz) in `src/order/order.entity.ts` and an `OrderService` in `src/order/order.service.ts` that receives an `OrderRepository` interface through an injection token.
