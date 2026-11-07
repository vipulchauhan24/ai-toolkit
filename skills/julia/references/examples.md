# Examples

## Example 1: An LP in a Julia package

User says: "write this LP in Julia": `allocate(costs, capacities, demand)` minimizes total cost with `sum(x) >= demand` and `0 <= x[i] <= capacities[i]`, returns a DataFrame, and is exposed as `GET /allocate`.

Actions:
1. Preflight: Python 3 and `scripts/check_julia.py` exist. Read `Project.toml` (Julia 1.10, JuMP, HiGHS, DataFrames) and the rules sections for those packages.
2. Run `Pkg.test()` once and note what already fails.
3. List the files to create. Write `allocate` in `src/services/allocate.jl`: a JuMP model with named variables, `set_silent`, the status check before reading values, and a DataFrame with columns `source` (Int) and `amount` (Float64). Write the tests: the optimum for costs `[3.0, 1.0, 2.0]`, capacities `[10.0, 5.0, 10.0]`, demand `12.0` is amounts `[0.0, 5.0, 7.0]`, and demand `100.0` raises an error.
4. Do not write the `GET /allocate` handler.
5. Verify: `Pkg.test()`, then `python3 -I scripts/check_julia.py <changed files>`. Fix every FAIL.

Result: status `done`, Julia version and packages read, files changed, checks run (lint, typecheck, build: none available), and the line `Boundaries: GET /allocate handler: api-builder needs allocate's signature and DataFrame columns`.

## Example 2: Blocked

User says: "write this LP in Julia" in an empty directory, non-interactively.

Actions: there is no `Project.toml`, so the project is not Julia. Stop before writing anything.

Result: a Blocked report that says what is blocked, why (`Project.toml` is missing from the project root), and what the caller must supply (a Julia project with a `Project.toml`). Nothing else.
