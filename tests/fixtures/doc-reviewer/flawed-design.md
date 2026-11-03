# Order Events Design

Audience: backend engineers on the checkout team.

## Overview

On checkout, the order service writes the order to MySQL and then publishes an OrderCreated event to Kafka for the downstream fulfilment and email services.

## Scale

The order service runs as a single instance behind the load balancer. Peak load is 50 orders per second today and we expect it to be fine for the next year.

## Rollout

We will switch all customers to the new flow on Saturday night. The old synchronous fulfilment call is removed in the same release.
