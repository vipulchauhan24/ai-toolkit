# clean-2.jl: a JuMP model with HiGHS.
using JuMP
using HiGHS
using DataFrames

function allocate(costs::Vector{Float64}, capacities::Vector{Float64}, demand::Float64)::DataFrame
    n = length(costs)
    model = Model(HiGHS.Optimizer)
    set_silent(model)
    @variable(model, 0 <= x[i = 1:n] <= capacities[i])
    @constraint(model, supply, sum(x) >= demand)
    @objective(model, Min, sum(costs[i] * x[i] for i in 1:n))
    optimize!(model)
    if termination_status(model) != MOI.OPTIMAL || primal_status(model) != MOI.FEASIBLE_POINT
        throw(ArgumentError("demand cannot be met: $(termination_status(model))"))
    end
    return DataFrame(source = collect(1:n), amount = value.(x))
end
