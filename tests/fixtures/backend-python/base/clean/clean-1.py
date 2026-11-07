"""Order model and service."""
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Order:
    id: uuid.UUID
    status: OrderStatus
    total_cents: int
    created_at: datetime
    note: Optional[str] = None


class OrderService:
    def __init__(self, clock) -> None:
        self._clock = clock

    def create(self, total_cents: int) -> Order:
        if total_cents < 0:
            raise ValueError("total_cents must be at least 0")
        logger.info("creating order")
        return Order(uuid.uuid4(), OrderStatus.PENDING, total_cents, self._clock())
