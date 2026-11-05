# Order service: design

## Summary

The order service accepts an order from the checkout page, stores it, and tells the rest of the company about it.

## Flow

1. The checkout page sends `POST /orders`.
2. The service inserts the order into its Postgres database.
3. The service then publishes an `order.created` event to the message queue.
4. The warehouse service and the email service consume `order.created`.

## Scale

The service runs as 3 instances behind a load balancer. We expect orders to grow and handle it by adding instances.

## Migration

Old orders live in the legacy MySQL database. On launch we switch checkout to the new service. Old orders are then available to the new service.
