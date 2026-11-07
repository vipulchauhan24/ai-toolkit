"""Order model and service for a FastAPI app."""
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Order:
    id: str
    total_cents: int
    note: Optional[str] = None


class OrderService:
    def __init__(self, store: dict) -> None:
        self._store = store

    def get(self, order_id: str) -> Optional[Order]:
        logger.info("loading order")
        return self._store.get(order_id)
