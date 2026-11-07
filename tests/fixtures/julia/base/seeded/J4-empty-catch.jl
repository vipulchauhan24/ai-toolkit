function read_value(path::String)
    try
        return read(path, String)
    catch e
    end
    try
        return parse(Int, "x")
    catch; end
    return nothing
end
