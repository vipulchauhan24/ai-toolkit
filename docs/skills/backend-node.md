# Backend Node Skill

The backend-node skill writes Node.js service code in TypeScript, with Express or NestJS, to a fixed set of rules and proves it with checks. It covers how the code is written: types, errors, concurrency, configuration, services and modules, entity classes, boundaries, logging, security and tests. It matches the project's own conventions first, and it runs the project's typecheck, lint, tests and build, then a Node check script.

It writes the entity classes for the tables in `schema.md` (or the phase document's data model). It does not write route handlers, controllers, middleware that shapes the API, queries, migrations or auth: api-builder and the database skills own those, and the skill reports each as the typed boundary.

## What You Need

- A Node.js project in TypeScript, with `package.json`, `tsconfig.json` and `typescript` as a dependency, and Express or NestJS as the server framework. The skill reads `package.json` to find the versions, the framework and the test runner, and follows what the project uses.
- **Python 3** (required). It runs the check script. Without it, the skill stops with a Blocked report before doing anything. It never falls back to searching files by hand.

## Using the Skill

In Claude Code, open the project and ask for the code:

- `build this in Node with Express`
- `write this NestJS service`
- `write the entity classes for the tables in schema.md`
- `add an OrderService with tests`
- `review this Node code against the rules`

With a phase document from project-planner, give its path. The skill builds only the scope the phase lists, types the data from the phase's data model, and reports acceptance criteria by number. It stops with a Blocked report if the phase pins a framework or a pattern the project doesn't match.

The skill detects NestJS from `@nestjs/core` (it wins over `express`, which Nest pulls in), else Express from `express`. A project with neither, with only `fastify` or another framework, with plain JavaScript, or with no `tsconfig.json` gets a Blocked report.

## Using it with other skills

The skills are independent and don't call each other. Name each skill you want in the prompt, for example `Use backend-node and api-builder to build the orders endpoint.` When two skills disagree, the skill that owns the topic wins, and the report lists each conflict and its winner.

The report has a `Boundaries` list for work this skill stopped at, each line `<boundary>: <owner skill> needs <file or contract>`, and says so when the owner is not installed.

## What the Skill Does Not Do

- It does not write route handlers, controllers, request validation, the error response shape, auth, queries or migrations.
- It does not support plain JavaScript, Fastify, Koa, Hono or other frameworks.
- It does not migrate a framework or a test setup, and it does not create a test setup.
- It does not follow instructions found inside project files. It follows the rules and the request.

## Customizing the Skill

- Edit `skills/backend-node/references/node-rules.md`, `express-rules.md` or `nestjs-rules.md` to change the rules. The three files are shared with api-builder: this skill holds the canonical copies. After editing, run `python3 scripts/check_shared_files.py --sync`.
- `architecture-patterns.md` is shared too: its canonical copy is in `skills/project-planner/references/`. Edit that one, then run the same command.
- Edit `scripts/check_node.py` to change the red flags it detects.

## Installing the Skill

### From the plugin marketplace

```text
/plugin marketplace add vipulchauhan24/ai-toolkit
/plugin install ai-toolkit@product-development
```

Invoke the skill with `/ai-toolkit:backend-node`, or let Claude pick it up from a matching prompt.

### Manually

Copy the `skills/backend-node/` folder to `.claude/skills/` in a project, or to `~/.claude/skills/` for all projects. It has no dependencies outside its own folder.

## License

MIT.
