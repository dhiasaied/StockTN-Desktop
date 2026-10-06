from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

@dataclass
class StockMovement:
    id: int
    product_id: int
    product_name: str
    movement_type: str  # entry | exit
    quantity: int
    reason: str
    user_id: int
    username: str
    date: str = ""
    reference: str = ""

    def __post_init__(self) -> None:
        if not self.date:
            self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StockMovement":
        return cls(
            id=int(data["id"]),
            product_id=int(data["product_id"]),
            product_name=data.get("product_name", ""),
            movement_type=data.get("movement_type", "entry"),
            quantity=int(data.get("quantity", 0)),
            reason=data.get("reason", ""),
            user_id=int(data.get("user_id", 0)),
            username=data.get("username", ""),
            date=data.get("date", ""),
            reference=data.get("reference", ""),
        )
