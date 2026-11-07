function run_code(code::String)
    return eval(Meta.parse(code))
end
