from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

@dataclass
class Supplier:
    id: int
    name: str
    phone: str = ""
    email: str = ""
    address: str = ""
    city: str = ""
    governorate: str = ""
    tax_id: str = ""
    active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Supplier":
        return cls(
            id=int(data["id"]),
            name=data.get("name", ""),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            address=data.get("address", ""),
            city=data.get("city", ""),
            governorate=data.get("governorate", ""),
            tax_id=data.get("tax_id", ""),
            active=bool(data.get("active", True)),
        )
