from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

@dataclass
class Product:
    id: int
    code: str
    barcode: str
    name: str
    category_id: int
    brand: str
    purchase_price: float
    sale_price: float
    quantity: int
    min_stock: int
    unit: str = "unité"
    description: str = ""
    image: str = ""
    active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Product":
        return cls(
            id=int(data["id"]),
            code=data.get("code", ""),
            barcode=data.get("barcode", ""),
            name=data.get("name", ""),
            category_id=int(data.get("category_id", 0)),
            brand=data.get("brand", ""),
            purchase_price=float(data.get("purchase_price", 0)),
            sale_price=float(data.get("sale_price", 0)),
            quantity=int(data.get("quantity", 0)),
            min_stock=int(data.get("min_stock", 0)),
            unit=data.get("unit", "unité"),
            description=data.get("description", ""),
            image=data.get("image", ""),
            active=bool(data.get("active", True)),
        )

    @property
    def is_out_of_stock(self) -> bool:
        return self.quantity <= 0

    @property
    def is_low_stock(self) -> bool:
        return 0 < self.quantity <= self.min_stock

    @property
    def stock_value(self) -> float:
        return self.quantity * self.purchase_price
