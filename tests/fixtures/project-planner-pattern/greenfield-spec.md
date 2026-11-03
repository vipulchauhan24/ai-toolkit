# Link Notes Service - Spec

- Status: ready to plan
- Version and date: v1, 2026-11-03
- Author and outcome owner: Vipul

## Overview

A small new FastAPI service that stores short notes attached to URLs. A single developer calls it from scripts to save a note and read it back.

### Success criteria

- Primary users or consumers: the developer, from curl and scripts
- Observable outcome that makes launch a success: a note saved for a URL is returned by a read call, measured by the tests passing
- Non-goals: accounts, search, a UI

## Requirements

### References and inspiration

- Reference: Not required: no external reference
- When a reference conflicts with a constraint, the winner is: the constraint

### Scope and features

- Form of the deliverable: API (service)
- Core capabilities:
  - Save note - must-have - Done when: `POST /notes` with a valid URL and text up to 500 characters returns 201 with the note, and an invalid URL returns 422
  - Read notes - must-have - Done when: `GET /notes?url=<url>` returns the notes saved for that URL, newest first
- Primary user or system actions: save a note, list notes for a URL
- Edge cases and failure behaviour: a URL with no notes returns an empty list

### Interfaces

- User interface: Not required: API only
- Programmatic interface: HTTP JSON, to be designed
  - Versioning and compatibility promise: Not required: single consumer
- Integrations with other systems: Not required: none
- How users get help or report problems: Not required: single developer

### Technology and constraints

- Engineering decisions already made: FastAPI, SQLite
  - Mark each item `fixed` (do not change), `preferred` (change only with a stated reason), or `planner decides`. An unmarked item is treated as `planner decides`.
  - Coding pattern: planner decides
- Stack: Python 3.12 and FastAPI, fixed; SQLite, fixed
- Existing code or systems to build on: greenfield
- Expected load: 1 request per second at launch, 10 at 10x
- Measurable quality bar before launch: p95 latency under 100 ms at 10 requests per second
- Constraints: none

### Data

- Where data comes from: user input
  - Required fields or schema: url (string, max 2048), text (string, max 500)
  - Behaviour when input violates the schema: reject with an error
- Personal or sensitive data stored or processed: None
- Where data is stored, and how long it is kept: SQLite file, kept until deleted by hand
- Volume at launch and expected growth: under 1,000 notes
- Does the real data or content exist today? no
  - If not, does launch wait for it? no
  - Placeholder data: none
  - Owner and date for replacing it: Not required
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

- Security: Not required: local only, no auth
- Privacy and compliance: Not required: no personal data
- Accessibility: Not required: no UI
- Reliability: Not required: local only
- Observability: Not required: local only
- Analytics or usage tracking: No
- Internationalization: English only
- Supported platforms and environments: Python 3.12
- Documentation: Not required: planner defaults
- Testing: Not required: planner defaults

## Open questions

None.
