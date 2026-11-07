# julia

## Should trigger

- "Write this LP in Julia."
- "Build a JuMP model that minimizes cost with HiGHS."
- "Write a Julia function that cleans this DataFrame."
- "Train a regression model in Julia with MLJ."
- "Analyze this CSV with DataFrames.jl and return the monthly totals."
- "Add a QP portfolio function to this Julia package."
- "Review this Julia code against the rules."
- "Write the Julia structs for the tables in schema.md."
- "Fix this type-unstable Julia function."
- "Build phase 6 of the plan in Julia." (with a phase document pinning Julia)

## Should NOT trigger

- "Write this in Python." (not Julia)
- "Build the Oxygen route handler for GET /allocate." (api-builder)
- "Write the SQL schema for users." (database skills)
- "Solve this mixed-integer problem with HiGHS.jl." (out of scope)
- "Train a neural network with Flux.jl." (out of scope)
- "Build a React dashboard for the results."
- "Pick colors and spacing for my app." (design-system-builder)
- "Explain what multiple dispatch is."
- "Build a Node.js service for orders." (backend-node)
- "Write the migration that adds an orders table." (database skills)

## Functional

**New LP function**
- Given: a Julia package with JuMP, HiGHS and DataFrames in `Project.toml`
- When: asked for `allocate(costs, capacities, demand)::DataFrame` and a `GET /allocate` endpoint, non-interactively
- Then: tests were run once before changes. `allocate` checks `termination_status` and `primal_status`, returns a DataFrame with columns `source` and `amount`, and has an optimum test and an infeasible-demand test. `Pkg.test()` passes. `scripts/check_julia.py` was run on the changed files with no FAIL. No route handler is written, and the report has the line `GET /allocate handler: api-builder needs allocate's signature and DataFrame columns`.

**Wrong stack**
- Given: a directory with no `Project.toml`
- When: asked to write Julia code, non-interactively
- Then: it stops with a Blocked report that names the missing `Project.toml` and writes no code.

**Missing Python**
- Given: no `python3` on the machine
- When: the skill starts
- Then: it stops with a Blocked report that names `python3`. It does not fall back to searching files by hand.

**Pinned pattern mismatch**
- Given: a phase document pinning `mvvm` and a codebase that uses `layered`
- When: run non-interactively
- Then: a Blocked report containing `Pattern mismatch`, and no code.

**Review only**
- Given: a Julia file with a `@show` and an empty `catch`
- When: asked to review it against the rules
- Then: the report lists each violation as `path:line` and the file is unchanged.
