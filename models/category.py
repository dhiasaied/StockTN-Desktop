from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

@dataclass
class Category:
    id: int
    name: str
    description: str = ""
    active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Category":
        return cls(
            id=int(data["id"]),
            name=data.get("name", ""),
            description=data.get("description", ""),
            active=bool(data.get("active", True)),
        )
