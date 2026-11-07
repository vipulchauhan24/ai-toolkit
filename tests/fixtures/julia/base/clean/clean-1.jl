# clean-1.jl: a struct and a function.
using Dates

struct Order
    id::Base.UUID
    total_cents::Int64
    placed_on::Dates.Date
    note::Union{String, Nothing}
end

"""Return the order total in whole currency units."""
function total_units(order::Order)::Float64
    return order.total_cents / 100
end
