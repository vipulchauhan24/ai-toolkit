# Julia Skill

The julia skill writes Julia code to a fixed set of rules and proves it with checks. It covers how the code is written for Oxygen service structure, DataFrames.jl, JuMP.jl with HiGHS.jl (LP and QP problems), model training with MLJ.jl and data analysis: types, errors, configuration, model structs, boundaries, logging, security and tests. It matches the project's own conventions first, and it runs the project's tests with `Pkg.test()` (Julia has no typecheck, lint or build step the skill can assume), then a Julia check script.

It writes the model structs for the tables in `schema.md` (or the phase document's data model). It does not write Oxygen route handlers, middleware, auth, queries or migrations: api-builder and the database skills own those, and the skill reports each as a typed boundary in the `Boundaries` list.

## What You Need

- A Julia project with a `Project.toml` in its root. The skill reads `[compat]` and `[deps]` to find the version and packages, and follows what the project uses. Julia 1.10 or later is needed to run the tests.
- **Python 3** (required). It runs the check script. Without it, the skill stops with a Blocked report before doing anything. It never falls back to searching files by hand.

## Using the Skill

In Claude Code, open the project and ask for the code:

- `write this LP in Julia`
- `build this in Julia`
- `analyze this CSV with DataFrames.jl`
- `train a model with MLJ.jl`
- `review this code against the Julia rules`

With a phase document from project-planner, give its path. The skill builds only the scope the phase lists, types the data from the phase's contracts, and reports acceptance criteria by number. It stops with a Blocked report if the phase pins a stack or a pattern the project doesn't match.

## Using it with other skills

The skills are independent and don't call each other. Name each skill you want in the prompt, for example `Use julia and api-builder to build the orders endpoint.` When two skills disagree, the skill that owns the topic wins, and the report lists each conflict and its winner.

## What the Skill Does Not Do

- It does not migrate a package or a test setup, and it does not create a test setup.
- It does not follow instructions found inside project files. It follows the rules and the request.
- It does not write Oxygen route handlers, queries, migrations or auth.
- It does not cover mixed-integer problems, Flux.jl or Lux.jl, and it never edits `Manifest.toml` or runs `Pkg.add`.
- It does not write mock servers. Where data doesn't exist yet, it types the expected shape and marks it `PLACEHOLDER-DATA`.

## Customizing the Skill

- Edit `skills/julia/references/julia-rules.md` to change the rules; it holds every Julia rule in sections for each package. `architecture-patterns.md` is shared: its canonical copy is in `skills/project-planner/references/`. Edit that one, then run `python3 scripts/check_shared_files.py --sync`.
- Edit `scripts/check_julia.py` to change the red flags it detects (rules J1 to J9). It has no framework flag.

## Installing the Skill

### From the plugin marketplace

```text
/plugin marketplace add vipulchauhan24/ai-toolkit
/plugin install ai-toolkit@product-development
```

Invoke the skill with `/ai-toolkit:julia`, or let Claude pick it up from a matching prompt.

### Manually

Copy the `skills/julia/` folder to `.claude/skills/` in a project, or to `~/.claude/skills/` for all projects. It has no dependencies outside its own folder.

## License

MIT.
