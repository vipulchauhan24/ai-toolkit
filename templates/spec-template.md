# <Project Name> - Spec

- Status: <draft / ready to plan / revised>
- Version and date: <v1, YYYY-MM-DD>
- Author and outcome owner: <name>

<!--
How to use

1. Never delete a line or heading. Answer it, or write one of these:
   - "Not required: <reason>" - the decision is made and there is no project-specific requirement.
   - "Undecided" - the decision is open. Add it to Open questions at the end.
   A missing line reads to the planner as an oversight, not a decision.
2. "Not required" does not switch off the planner's standing rules for validation, errors, tests, migrations, and documentation. They still apply unless a line here explicitly overrides one.
3. Small project (script, one-off tool, small library)? Fill Overview, Scope and features, Technology and constraints, and Delivery and operations. Answer each remaining section with a single "Not required: <reason>".
4. Replace every <placeholder> with a concrete answer. Prefer numbers, names, and links over adjectives. Link to references (screenshots, docs, repos) instead of describing them.
5. Add sections the project needs. The last section lists prompts by project type to copy from.
-->

## Overview

<One or two sentences: what is being built, who or what uses it, and the value it delivers.>

### Success criteria

- Primary users or consumers: <the people, teams, or systems the project must serve first; if there are several, rank them>
- Observable outcome that makes launch a success: <a measurable result, with a number, a timeframe, and the baseline it is measured against; if there is no baseline, say how it will be measured>
- Non-goals: <what is explicitly out of scope; the only list of exclusions>

## Requirements

### References and inspiration

- Reference: <product, repo, document, or prior work to take inspiration from> (<link>)
  - Taken from it: <the specific part to reuse, such as a flow, interface, behaviour, or architecture> (<link or screenshot>)
- When a reference conflicts with <standard / existing system / constraint>, the winner is: <name>

### Scope and features

- Form of the deliverable: <such as a web app, mobile app, CLI, library, API, service, data pipeline, or a combination>
- Core capabilities: <one entry per capability, in the format below>
  - Priority describes importance, not build order. The planner orders the build by dependency and risk.
  - Format: `<Capability name> - <must-have / should-have / nice-to-have> - Done when: <binary, testable statements, with real numbers where relevant>`
  - Example: `Create short link - must-have - Done when: a valid URL returns a 7-character code in under 200 ms, and an invalid URL returns a 400 with an error message`
- Primary user or system actions: <what a user or calling system must be able to do, and the expected result of each>
- Edge cases and failure behaviour: <inputs or conditions that need defined handling, and what happens for each>

### Interfaces

Describe every surface the project exposes.

- User interface: <screens, pages, or views in order>
  - Design system or visual standard: <name and link, version to pin, or "none">
  - Themes, platforms, and screen sizes: <what must be supported>
- Programmatic interface: <API, SDK, CLI commands, events, or file formats, with a link to the contract or "to be designed">
  - Versioning and compatibility promise: <approach>
- Integrations with other systems: <each system, the direction of data, and who owns it>
- How users get help or report problems: <channel>

### Technology and constraints

- Engineering decisions already made: <architecture, data model, key libraries, or "None">
  - Mark each item `fixed` (do not change), `preferred` (change only with a stated reason), or `planner decides`. An unmarked item is treated as `planner decides`.
- Stack: <languages, frameworks, runtime, and platforms, each marked fixed / preferred / planner decides>
- Existing code or systems to build on: <repo or system and link, or "greenfield">
- Expected load: <users, request rate, concurrency, and data size at launch and at 10x; or how it will be measured and the default to assume until then>
- Measurable quality bar before launch: <metric, target, and the load it must hold under, such as "p95 latency under 200 ms at 100 requests per second">
- Constraints: <mandated tools, services, versions, licences, budget, or hardware>

### Data

- Where data comes from: <files / database / external API / user input / manual entry>
  - Required fields or schema: <field names, and which are required>
  - Behaviour when input violates the schema: <fail / skip / reject with an error>
- Personal or sensitive data stored or processed: <list each field, or "None">
- Where data is stored, and how long it is kept: <storage and retention period, including deletion>
- Volume at launch and expected growth: <numbers>
- Does the real data or content exist today? <yes / no>
  - If not, does launch wait for it? <yes / no>
  - Placeholder data: <what is used instead, and what stops it from shipping>
  - Owner and date for replacing it: <name and date>
- Migration from an existing system: <what moves, how it is verified, and how it is reversed>

### Delivery and operations

- Delivery type: <deployed (service, app, bot, job) / published (library, SDK, CLI, plugin) / not delivered (internal script, one-off tool, local only)>
  - If not delivered, answer the later lines in this section "Not required: not delivered".
- How the project is shipped: <deploy target, package registry, app store, or distribution method>
  - Branch or version that maps to production: <branch name or release process>
  - Checks that must pass before a release: <build / lint / tests / review / none>
  - Rollback approach: <approach>
- Environments and secrets: <list of environments and where secrets are stored, or "none">
- Monitoring and alerting: <what is watched, and who is notified>
- Ownership after launch: <who maintains it>

### Team, dependencies, and timeline

- Who builds it: <an agent alone / one engineer plus an agent / a team, and how many people>
- Approver for each phase or release: <name or role>
- External dependencies: <each item the build needs from outside it, such as an API key, an account, a vendor, another team's service or decision. For each: the item, its owner, and the date it is needed by. Or "None">
- Target date and flexibility: <date, and whether the date or the scope gives way if they conflict>

## Cross-cutting

- Security:
  - Roles and permissions: <each role and what it may do, or "single user / no roles">
  - Untrusted inputs and misuse limits: <which inputs come from outside, and how abuse is limited, such as rate limits, quotas, size limits, or spam handling>
  - Authentication and data-handling requirements: <approach>
- Privacy and compliance: <consent, regulatory needs, and deletion requests, based on the personal data listed in Data; write "Not required: no personal data" only if Data says "None">
- Accessibility: <standard to meet, such as WCAG 2.2 AA>
- Reliability: <uptime, recovery, and backup targets at the expected load>
- Observability: <logging, metrics, and tracing needs>
- Analytics or usage tracking: <tool and events, or "No">
- Internationalization: <languages and locales, or "English only">
- Supported platforms and environments: <minimum OS, browser, device, or runtime versions>
- Documentation: <what docs must ship, such as a README, API reference, or user guide>
- Testing: <levels expected beyond the planner's defaults, such as end-to-end or load tests, or "Not required: planner defaults">

## Open questions

Every undecided line above belongs here. The planner asks you about high-stakes questions before writing the affected phase, and assumes the stated default for the rest.

| Question | Options | Decider | Needed by | If unanswered |
| -------- | ------- | ------- | --------- | ------------- |
| <decision still to be made> | <the options> | <name or role> | <date or phase> | <"ask me first", or the default the planner may assume> |

## Project-type prompts

Copy the lines that apply into the sections above, or into a new section. Delete the rest when the spec is final.

### Web site or web app

- Content source and schema: <files in the repo / CMS / database / API, and required fields>
- URL structure or routes: <each route pattern>
- Rendering model: <SSG / SSR / SPA>
- Themes: <default theme, what a first-time and a returning visitor see, where the choice persists, and how a flash of the wrong theme on first load is avoided>
- Responsive targets: <breakpoints or devices that must work>
- Discoverability: <metadata / Open Graph / sitemap / canonical URLs / structured data>
- Performance: <Lighthouse score or Core Web Vitals targets>
- Domain, DNS, and canonical host: <domain, and www or apex>
- Contact or support form: <where submissions go, and spam handling>
- Error and empty states: <404 page, offline state, and failure messages, with a link to a design>

### Mobile app

- Platforms and minimum OS versions: <iOS / Android versions>
- Offline behaviour and sync: <what works offline, and how conflicts are resolved>
- Permissions requested: <each permission and why>
- Store listing and review requirements: <accounts, assets, and policies>
- Push notifications: <events, and opt-in behaviour>

### API or service

- Contract format: <OpenAPI / GraphQL schema / protobuf, and where it lives>
- Authentication for callers: <API keys / OAuth / mTLS>
- Pagination, rate limits, and idempotency: <rules>
- Deprecation policy: <how long old versions are supported>

### Library, SDK, or CLI

- Public API surface: <names, signatures, types, and errors, or a link>
- Supported runtimes and versions: <list>
- Semantic versioning policy: <what counts as breaking>
- Usage examples required: <list>
- CLI conventions: <flags, exit codes, output formats, and config file locations>

### Data pipeline or batch job

- Sources and sinks: <each, with format and access method>
- Schedule and latency: <cadence and the freshness target>
- Idempotency and re-run behaviour: <what happens when a run repeats or fails halfway>
- Data quality checks: <checks and what happens on failure>
- Backfill: <how historical data is loaded>
