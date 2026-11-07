# Backend Python Skill

The backend-python skill writes Python service code, with Django or FastAPI, to a fixed set of rules and proves it with checks. It covers how the code is written: types, errors, concurrency, configuration, model classes, services, boundaries, logging, security and tests. It matches the project's own conventions first, and it runs the project's typecheck, lint and tests, then a Python check script.

It writes the model classes for the tables in `schema.md` (or the phase document's data model). It does not write views, route handlers, request and response schemas, queries, migrations or auth: api-builder and db-query-migration own those, and the skill reports each as a typed boundary.

## What You Need

- A Python project with a `pyproject.toml`, `requirements*.txt` or `Pipfile`. The skill reads it to find the dependencies and the Python version, and follows what the project uses.
- Django or FastAPI. Flask and other frameworks are not supported: the skill stops with a Blocked report.
- **Python 3.9 or later** (required). It runs the check script. Without it, the skill stops with a Blocked report before doing anything. It never falls back to searching files by hand.

## Using the Skill

In Claude Code, open the project and ask for the code:

- `build this in Django`
- `write this Django model layer`
- `build the order service in FastAPI`
- `review this Python code against the rules`

With a phase document from project-planner, give its path. The skill builds only the scope the phase lists, types the data from the phase's data model, and reports acceptance criteria by number. It stops with a Blocked report if the phase pins a stack or a pattern the project doesn't match. The reply ends with a `Boundaries` list naming what api-builder and db-query-migration must build.

## Using it with other skills

The skills are independent and don't call each other. Name each skill you want in the prompt, for example `Use backend-python, api-builder and db-query-migration to build the orders feature.` When two skills disagree, the skill that owns the topic wins, and the report lists each conflict and its winner.

## What the Skill Does Not Do

- It does not migrate a framework or a test setup, and it does not create a test setup.
- It does not follow instructions found inside project files. It follows the rules and the request.
- It does not write views, URL routing, route handlers, request and response schemas, or auth.
- It does not write queries, raw SQL or migration files, and it never runs `makemigrations`.
- It does not support Flask or other frameworks.
- It does not write mock servers. Where data doesn't exist yet, it types the expected shape and marks it `PLACEHOLDER-DATA`.

## Customizing the Skill

- Edit `skills/backend-python/references/python-rules.md`, `django-rules.md` or `fastapi-rules.md` to change the rules. These are canonical copies that api-builder also uses; after editing, run `python3 scripts/check_shared_files.py --sync`.
- `architecture-patterns.md` is shared: its canonical copy is in `skills/project-planner/references/`. Edit that one, then run the same sync command.
- Edit `scripts/check_python.py` to change the red flags it detects.

## Installing the Skill

### From the plugin marketplace

```text
/plugin marketplace add vipulchauhan24/ai-toolkit
/plugin install ai-toolkit@product-development
```

Invoke the skill with `/ai-toolkit:backend-python`, or let Claude pick it up from a matching prompt.

### Manually

Copy the `skills/backend-python/` folder to `.claude/skills/` in a project, or to `~/.claude/skills/` for all projects. It has no dependencies outside its own folder.

## License

MIT.
