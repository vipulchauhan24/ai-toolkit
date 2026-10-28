# <Project Name> - PRD

<!--
How to use: replace every <placeholder> with a concrete answer. Delete a bullet or section that does not apply to the project, and add sections the project needs. Write "Not required" or "No" rather than leaving a line blank: an explicit answer tells the planner the decision is made. Link to references (screenshots, docs, repos) instead of describing them.
-->

## Overview

<One or two sentences: what is being built, who or what uses it, and the value it delivers.>

### Success criteria

- Primary users or consumers: <the people, teams, or systems the project must serve first>
- Observable outcome that makes launch a success: <a measurable result, with a number and a timeframe>
- Non-goals: <what is explicitly out of scope>

## Requirements

### References and inspiration

- Reference: <product, repo, document, or prior work to take inspiration from> (<link>)
  - Taken from it: <the specific part to reuse, such as a flow, interface, behaviour, or architecture> (<link or screenshot>)
- When a reference conflicts with <standard / existing system / constraint>, the winner is: <name>

### Scope and features

- Form of the deliverable: <such as a web app, mobile app, CLI, library, API, service, data pipeline, or a combination>
- Core capabilities, in priority order: <each capability, with the must-haves marked>
- Primary user or system actions: <what a user or calling system must be able to do, and the expected result of each>
- Out of scope: <features not to build>
- Edge cases and failure behaviour: <inputs or conditions that need defined handling, and what happens for each>

### Interfaces

Describe every surface the project exposes. Delete the ones that do not apply.

- User interface: <screens, pages, or views in order, or "none">
  - Design system or visual standard: <name and link, version to pin, or "none">
  - Themes, platforms, and screen sizes: <what must be supported>
- Programmatic interface: <API, SDK, CLI commands, events, or file formats, with a link to the contract or "to be designed">
  - Versioning and compatibility promise: <approach, or "Not required">
- Integrations with other systems: <each system, the direction of data, and who owns it>
- How users get help or report problems: <channel, or "Not required">

### Technology and constraints

- Stack: <languages, frameworks, runtime, and platforms, or "planner's choice">
- Measurable quality bar before launch: <metric and target, such as latency, throughput, load time, memory, or test coverage>
- Constraints: <mandated tools, services, versions, licences, budget, hardware, or deadlines>
- Existing code or systems to build on: <repo or system and link, or "greenfield">

### Data

- Where data comes from: <files / database / external API / user input / manual entry>
  - Required fields or schema: <field names, and which are required>
  - Behaviour when input violates the schema: <fail / skip / reject with an error>
- Where data is stored and for how long: <storage and retention>
- Volume at launch and expected growth: <numbers>
- Does the real data or content exist today? <yes / no>
  - If not, does launch wait for it? <yes / no>
  - Placeholder data: <what is used instead, and what stops it from shipping>
  - Owner and date for replacing it: <name and date, or "Not required">
- Migration from an existing system: <what moves, and how, or "Not required">

### Delivery and operations

- How the project is shipped: <deploy target, package registry, app store, or distribution method>
  - Branch or version that maps to production: <branch name or release process>
  - Checks that must pass before a release: <build / lint / tests / review / none>
  - Rollback approach: <approach, or "Not required">
- Environments and secrets: <list of environments and where secrets are stored, or "none">
- Monitoring and alerting: <what is watched, and who is notified, or "Not required">
- Ownership after launch: <who maintains it, or "Not required">

## Cross-cutting

- Security: <authentication, authorization, and data-handling requirements, or "Not applicable">
- Privacy and compliance: <consent, retention, and regulatory needs, or "No">
- Accessibility: <standard to meet, such as WCAG 2.2 AA, or "Not applicable">
- Reliability: <uptime, recovery, or backup targets, or "Not required">
- Observability: <logging, metrics, and tracing needs, or "Not required">
- Analytics or usage tracking: <tool and events, or "No">
- Internationalization: <languages and locales, or "English only">
- Supported platforms and environments: <minimum OS, browser, device, or runtime versions>
- Documentation: <what docs must ship, such as a README, API reference, or user guide>
- Testing: <levels expected, such as unit, integration, and end-to-end, and who writes them>

## Open questions

- <Decision still to be made, the options, and who decides>
