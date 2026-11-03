# Order Cancellation - Spec

- Status: ready to plan
- Version and date: v1, 2026-11-03
- Author and outcome owner: Vipul

## Overview

Add order cancellation to the existing orders API in `sample-project/`. A customer's backend calls the API to cancel an order that has not shipped.

### Success criteria

- Primary users or consumers: the storefront backend that calls the orders API
- Observable outcome that makes launch a success: a placed order can be cancelled with one call, and a shipped order cannot; measured by the tests in the cancellation phase
- Non-goals: refunds, notifications, bulk cancellation

## Requirements

### References and inspiration

- Reference: Not required: no external reference
- When a reference conflicts with an existing system, the winner is: the existing system

### Scope and features

- Form of the deliverable: API (extends the existing Express service)
- Core capabilities:
  - Cancel order - must-have - Done when: `POST /orders/:id/cancel` on a placed order returns 200 with status `cancelled`, on a shipped order returns 409, on an unknown id returns 404
- Primary user or system actions: cancel an order by id
- Edge cases and failure behaviour: cancelling an already cancelled order returns 200 and changes nothing

### Interfaces

- User interface: Not required: API only
- Programmatic interface: HTTP JSON, to be designed
  - Versioning and compatibility promise: no breaking change to existing endpoints
- Integrations with other systems: Not required: none
- How users get help or report problems: Not required: internal service

### Technology and constraints

- Engineering decisions already made: build on the existing codebase
  - Mark each item `fixed` (do not change), `preferred` (change only with a stated reason), or `planner decides`. An unmarked item is treated as `planner decides`.
  - Coding pattern: planner decides
- Stack: the existing stack, fixed
- Existing code or systems to build on: `sample-project/` in this folder
- Expected load: 10 requests per second at launch, 100 at 10x
- Measurable quality bar before launch: p95 latency under 200 ms at 10 requests per second
- Constraints: none

### Data

- Where data comes from: user input
  - Required fields or schema: order id
  - Behaviour when input violates the schema: reject with an error
- Personal or sensitive data stored or processed: None
- Where data is stored, and how long it is kept: in memory, until restart
- Volume at launch and expected growth: under 1,000 orders
- Does the real data or content exist today? no
  - If not, does launch wait for it? no
  - Placeholder data: in-memory store
  - Owner and date for replacing it: Vipul, undecided
- Migration from an existing system: Not required: none

### Delivery and operations

- Delivery type: not delivered (local only)
  - If not delivered, answer the later lines in this section "Not required: not delivered".

### Team, dependencies, and timeline

- Who builds it: an agent alone
- Approver for each phase or release: Vipul
- External dependencies: None
- Target date and flexibility: none

## Cross-cutting

- Security: Not required: internal, no auth in this spec
- Privacy and compliance: Not required: no personal data
- Accessibility: Not required: no UI
- Reliability: Not required: local only
- Observability: Not required: local only
- Analytics or usage tracking: No
- Internationalization: English only
- Supported platforms and environments: Node 20
- Documentation: Not required: planner defaults
- Testing: Not required: planner defaults

## Open questions

None.
