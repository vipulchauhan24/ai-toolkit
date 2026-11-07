using LibPQ

function connect_db(url::String)
    return LibPQ.Connection(url)
end
