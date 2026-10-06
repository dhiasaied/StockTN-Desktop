from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional

@dataclass
class User:
    id: int
    username: str
    password_hash: str
    role: str  # admin | seller | client
    active: bool = True
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    customer_id: Optional[int] = None  # lien compte client

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "User":
        return cls(
            id=int(data["id"]),
            username=data["username"],
            password_hash=data["password_hash"],
            role=data.get("role", "client"),
            active=bool(data.get("active", True)),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            customer_id=data.get("customer_id"),
        )

    @property
    def full_name(self) -> str:
        name = f"{self.first_name} {self.last_name}".strip()
        return name or self.username
