def load(raw: str) -> int:
    try:
        return int(raw)
    except ValueError:
        pass
    return 0
