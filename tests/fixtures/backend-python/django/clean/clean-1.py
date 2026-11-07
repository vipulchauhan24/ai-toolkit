"""Order model for a Django app."""
import uuid

from django.db import models


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    CANCELLED = "cancelled", "Cancelled"


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    status = models.TextField(choices=OrderStatus.choices)
    total_cents = models.IntegerField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = "orders"

    def __str__(self) -> str:
        return str(self.id)
