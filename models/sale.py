from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Optional

@dataclass
class SaleItem:
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
    def from_dict(cls, data: dict[str, Any]) -> "SaleItem":
        return cls(
            product_id=int(data["product_id"]),
            product_code=data.get("product_code", ""),
            product_name=data.get("product_name", ""),
            quantity=int(data.get("quantity", 0)),
            unit_price=float(data.get("unit_price", 0)),
        )

@dataclass
class Sale:
    id: int
    items: list[SaleItem] = field(default_factory=list)
    customer_id: Optional[int] = None
    customer_name: str = "Client comptoir"
    user_id: int = 0
    username: str = ""
    date: str = ""
    total: float = 0.0
    payment_method: str = "Espèces"
    note: str = ""

    def __post_init__(self) -> None:
        if not self.date:
            self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.items and not self.total:
            self.recalculate()

    def recalculate(self) -> None:
        self.total = sum(item.total for item in self.items)

    def to_dict(self) -> dict[str, Any]:
        self.recalculate()
        return {
            "id": self.id,
            "items": [i.to_dict() for i in self.items],
            "customer_id": self.customer_id,
            "customer_name": self.customer_name,
            "user_id": self.user_id,
            "username": self.username,
            "date": self.date,
            "total": self.total,
            "payment_method": self.payment_method,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Sale":
        items = [SaleItem.from_dict(i) for i in data.get("items", [])]
        return cls(
            id=int(data["id"]),
            items=items,
            customer_id=data.get("customer_id"),
            customer_name=data.get("customer_name", "Client comptoir"),
            user_id=int(data.get("user_id", 0)),
            username=data.get("username", ""),
            date=data.get("date", ""),
            total=float(data.get("total", 0)),
            payment_method=data.get("payment_method", "Espèces"),
            note=data.get("note", ""),
        )
