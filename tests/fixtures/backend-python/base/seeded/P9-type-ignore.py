import json


def load(raw: str) -> int:
    return json.loads(raw)  # type: ignore
