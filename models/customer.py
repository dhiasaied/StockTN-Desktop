from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Optional

@dataclass
class Customer:
    id: int
    last_name: str
    first_name: str
    phone: str = ""
    email: str = ""
    address: str = ""
    city: str = ""
    created_at: str = ""
    user_id: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Customer":
        return cls(
            id=int(data["id"]),
            last_name=data.get("last_name", ""),
            first_name=data.get("first_name", ""),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            address=data.get("address", ""),
            city=data.get("city", ""),
            created_at=data.get("created_at", ""),
            user_id=data.get("user_id"),
        )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
