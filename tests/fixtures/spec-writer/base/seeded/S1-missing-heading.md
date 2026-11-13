# Sample Service - Spec

- Status: ready to plan
- Version and date: v1, 2026-11-07
- Author and outcome owner: Vipul Chauhan

## Overview

A small service that stores orders and reports counts, used by the checkout page.

### Success criteria

- Primary users or consumers: Not required: fixture
- Observable outcome that makes launch a success: Not required: fixture
- Figures that are results, not targets: Not required: fixture
- Non-goals: Not required: fixture

## Requirements

### References and inspiration

- Reference: Not required: fixture
  - Taken from it: Not required: fixture
- When a reference conflicts with a standard or constraint, the winner is: the constraint

### Scope and features

- Form of the deliverable: Not required: fixture
- Core capabilities: one entry per capability
  - Save order - must-have - Done when: a valid order returns 201 in under 200 ms, and an invalid order returns a 400 with an error message
- Primary user or system actions: Not required: fixture
- Edge cases and failure behaviour: Not required: fixture

### Interfaces

Describe every surface the project exposes.

- User interface: Not required: fixture
  - Page kind: Not required: fixture
  - The one action each page leads to: Not required: fixture
  - Audience: Not required: fixture
  - Look inputs: Not required: fixture
  - Platforms and screen sizes: Not required: fixture
- Programmatic interface: Not required: fixture
  - Versioning and compatibility promise: Not required: fixture
- Integrations with other systems: Not required: fixture
- How users get help or report problems: Not required: fixture

### Technology and constraints

- Engineering decisions already made: Not required: fixture
  - Coding pattern: Not required: fixture
- Stack: Undecided
- Existing code or systems to build on: Not required: fixture
- Expected load: Not required: fixture
- Measurable quality bar before launch: Not required: fixture
- Constraints: Not required: fixture

### Data

- Where data comes from: Not required: fixture
  - Required fields or schema: Not required: fixture
  - Behaviour when input violates the schema: Not required: fixture
- Personal or sensitive data stored or processed: Not required: fixture
- Where data is stored, and how long it is kept: Not required: fixture
- Volume at launch and expected growth: Not required: fixture
- Does the real data or content exist today? no
  - If not, does launch wait for it? no
  - Content that does not exist yet: Not required: fixture
  - Owner and date for replacing it: Not required: fixture
- Migration from an existing system: Not required: fixture

### Delivery and operations

- Delivery type: Not required: fixture
- How the project is shipped: Not required: fixture
  - Branch or version that maps to production: Not required: fixture
  - Checks that must pass before a release: Not required: fixture
  - Rollback approach: Not required: fixture
- Environments and secrets: Not required: fixture
- Monitoring and alerting: Not required: fixture
- Ownership after launch: Not required: fixture

### Team, dependencies, and timeline

- Who builds it: Not required: fixture
- Approver for each phase or release: Not required: fixture
- External dependencies: Not required: fixture
- Target date and flexibility: Not required: fixture


- Security:
  - Roles and permissions: Not required: fixture
  - Untrusted inputs and misuse limits: Not required: fixture
  - Authentication and data-handling requirements: Not required: fixture
- Privacy and compliance: Not required: fixture
- Accessibility: Not required: fixture
- Reliability: Not required: fixture
- Observability: Not required: fixture
- Analytics or usage tracking: Not required: fixture
- Internationalization: Not required: fixture
- Supported platforms and environments: Not required: fixture
- Documentation: Not required: fixture
- Testing: Not required: fixture

## Open questions

Every undecided line above belongs here. The planner asks you about high-stakes questions before writing the affected phase, and assumes the stated default for the rest.

| Question | Options | Decider | Needed by | If unanswered |
| -------- | ------- | ------- | --------- | ------------- |
| Which stack to use | Node.js, Python | Vipul | Phase 1 | Ask me first |
