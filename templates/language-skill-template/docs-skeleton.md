# <<TITLE>> Skill

The <<NAME>> skill writes <<LANG>> code to a fixed set of rules and proves it with checks. It covers how the code is written: types, errors, concurrency, configuration, entity and model classes, boundaries, logging, security and tests. It matches the project's own conventions first, and it runs the project's typecheck, lint, tests and build, then a <<LANG>> check script.

It writes the entity and model classes for the tables in `schema.md` (or the phase document's data model). It does not write route handlers, controllers, queries, migrations or auth: api-builder and the database skills own those, and the skill reports each as the typed boundary.

## What You Need

- A <<LANG>> project. The skill reads `<<PROJECT_FILE>>` to find the version and dependencies, and follows what the project uses.
- **Python 3** (required). It runs the check script. Without it, the skill stops with a Blocked report before doing anything. It never falls back to searching files by hand.

## Using the Skill

In Claude Code, open the project and ask for the code:

- <<TRIGGERS>>
- `review this code against the <<LANG>> rules`

With a phase document from project-planner, give its path. The skill builds only the scope the phase lists, types the data from the phase's contracts, and reports acceptance criteria by number. It stops with a Blocked report if the phase pins a stack or a pattern the project doesn't match.

## Using it with other skills

The skills are independent and don't call each other. Name each skill you want in the prompt, for example `Use <<NAME>> and api-builder to build the orders endpoint.` When two skills disagree, the skill that owns the topic wins, and the report lists each conflict and its winner.

## What the Skill Does Not Do

- It does not migrate a framework or a test setup, and it does not create a test setup.
- It does not follow instructions found inside project files. It follows the rules and the request.
- It does not write route handlers, controllers, queries, migrations or auth.
- It does not write mock servers. Where data doesn't exist yet, it types the expected shape and marks it `PLACEHOLDER-DATA`.

## Customizing the Skill

- Edit `skills/<<NAME>>/references/<<RULES>>` to change the rules. `architecture-patterns.md` is shared: its canonical copy is in `skills/project-planner/references/`. Edit that one, then run `python3 scripts/check_shared_files.py --sync`.
- Edit `scripts/check_LANG.py` to change the red flags it detects.

## Installing the Skill

### From the plugin marketplace

```text
/plugin marketplace add vipulchauhan24/ai-toolkit
/plugin install ai-toolkit@product-development
```

Invoke the skill with `/ai-toolkit:<<NAME>>`, or let Claude pick it up from a matching prompt.

### Manually

Copy the `skills/<<NAME>>/` folder to `.claude/skills/` in a project, or to `~/.claude/skills/` for all projects. It has no dependencies outside its own folder.

## License

MIT.
