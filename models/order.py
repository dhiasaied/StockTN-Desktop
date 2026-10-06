from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

ORDER_STATUSES = [
    "En attente",
    "Confirmée",
    "En préparation",
    "Prête",
    "Terminée",
    "Annulée",
]

@dataclass
class OrderItem:
    product_id: int
    product_code: str
    product_name: str
    quantity: int
    unit_price: float

    @property
    def total(self) -> float:
        return self.quantity * self.unit_price

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["total"] = self.total
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrderItem":
        return cls(
            product_id=int(data["product_id"]),
            product_code=data.get("product_code", ""),
            product_name=data.get("product_name", ""),
            quantity=int(data.get("quantity", 0)),
            unit_price=float(data.get("unit_price", 0)),
        )

@dataclass
class Order:
    id: int
    customer_id: int
    customer_name: str = ""
    items: list[OrderItem] = field(default_factory=list)
    status: str = "En attente"
    date: str = ""
    updated_at: str = ""
    total: float = 0.0
    note: str = ""

    def __post_init__(self) -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.date:
            self.date = now
        if not self.updated_at:
            self.updated_at = now
        if self.items and not self.total:
            self.recalculate()

    def recalculate(self) -> None:
        self.total = sum(item.total for item in self.items)

    def to_dict(self) -> dict[str, Any]:
        self.recalculate()
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "customer_name": self.customer_name,
            "items": [i.to_dict() for i in self.items],
            "status": self.status,
            "date": self.date,
            "updated_at": self.updated_at,
            "total": self.total,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Order":
        items = [OrderItem.from_dict(i) for i in data.get("items", [])]
        return cls(
            id=int(data["id"]),
            customer_id=int(data.get("customer_id", 0)),
            customer_name=data.get("customer_name", ""),
            items=items,
            status=data.get("status", "En attente"),
            date=data.get("date", ""),
            updated_at=data.get("updated_at", ""),
            total=float(data.get("total", 0)),
            note=data.get("note", ""),
        )
