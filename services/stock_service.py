from __future__ import annotations

from models.stock_movement import StockMovement
from services.product_service import ProductService
from utils.json_storage import JsonStorage
from utils.validators import require_non_empty, validate_int

class StockService:
    FILE = "stock_movements.json"

    def __init__(self, storage: JsonStorage, product_service: ProductService) -> None:
        self.storage = storage
        self.products = product_service
        if not self.storage.path_for(self.FILE).exists():
            self.storage.save(self.FILE, [])

    def _all(self) -> list[StockMovement]:
        return [
            StockMovement.from_dict(m)
            for m in self.storage.load(self.FILE, default=[])
        ]

    def _save(self, movements: list[StockMovement]) -> None:
        self.storage.save(self.FILE, [m.to_dict() for m in movements])

    def get_all(self) -> list[StockMovement]:
        return sorted(self._all(), key=lambda m: m.date, reverse=True)

    def get_by_product(self, product_id: int) -> list[StockMovement]:
        return [m for m in self.get_all() if m.product_id == product_id]

    def add_entry(
        self,
        product_id: int,
        quantity: int,
        reason: str,
        user_id: int,
        username: str,
        reference: str = "",
    ) -> StockMovement:
        quantity = validate_int(quantity, "Quantité", 1)
        reason = require_non_empty(reason, "Motif")
        product = self.products.adjust_quantity(product_id, quantity)
        movement = StockMovement(
            id=self.storage.next_id(self.FILE),
            product_id=product.id,
            product_name=product.name,
            movement_type="entry",
            quantity=quantity,
            reason=reason,
            user_id=user_id,
            username=username,
            reference=reference,
        )
        movements = self._all()
        movements.append(movement)
        self._save(movements)
        return movement

    def add_exit(
        self,
        product_id: int,
        quantity: int,
        reason: str,
        user_id: int,
        username: str,
        reference: str = "",
    ) -> StockMovement:
        quantity = validate_int(quantity, "Quantité", 1)
        reason = require_non_empty(reason, "Motif")
        product = self.products.adjust_quantity(product_id, -quantity)
        movement = StockMovement(
            id=self.storage.next_id(self.FILE),
            product_id=product.id,
            product_name=product.name,
            movement_type="exit",
            quantity=quantity,
            reason=reason,
            user_id=user_id,
            username=username,
            reference=reference,
        )
        movements = self._all()
        movements.append(movement)
        self._save(movements)
        return movement
