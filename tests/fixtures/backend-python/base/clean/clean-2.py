"""Parsing helpers with specific error handling."""
import json
import logging
from typing import List, Optional, TypedDict

logger = logging.getLogger(__name__)


class Address(TypedDict):
    street: str
    city: str


def parse_address(raw: str) -> Address:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as err:
        logger.warning("bad address payload")
        raise ValueError("address is not valid JSON") from err
    return Address(street=str(data["street"]), city=str(data["city"]))


def collect(items: List[str], seen: Optional[List[str]] = None) -> List[str]:
    result = [] if seen is None else list(seen)
    result.extend(items)
    return result


def test_collect() -> None:
    assert collect(["a"]) == ["a"]
