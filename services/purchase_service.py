from __future__ import annotations

from datetime import datetime
from typing import Optional

from models.purchase import Purchase, PurchaseItem
from models.user import User
from services.product_service import ProductService
from services.stock_service import StockService
from services.supplier_service import SupplierService
from utils.json_storage import JsonStorage
from utils.validators import validate_int, validate_positive_number

class PurchaseService:
    FILE = "purchases.json"

    def __init__(
        self,
        storage: JsonStorage,
        product_service: ProductService,
        stock_service: StockService,
        supplier_service: SupplierService,
    ) -> None:
        self.storage = storage
        self.products = product_service
        self.stock = stock_service
        self.suppliers = supplier_service
        if not self.storage.path_for(self.FILE).exists():
            self.storage.save(self.FILE, [])

    def _all(self) -> list[Purchase]:
        return [
            Purchase.from_dict(p) for p in self.storage.load(self.FILE, default=[])
        ]

    def _save(self, purchases: list[Purchase]) -> None:
        self.storage.save(self.FILE, [p.to_dict() for p in purchases])

    def get_all(self) -> list[Purchase]:
        return sorted(self._all(), key=lambda p: p.date, reverse=True)

    def get_by_id(self, purchase_id: int) -> Optional[Purchase]:
        for p in self._all():
            if p.id == purchase_id:
                return p
        return None

    def get_today(self) -> list[Purchase]:
        today = datetime.now().strftime("%Y-%m-%d")
        return [p for p in self.get_all() if p.date.startswith(today)]

    def get_month(self) -> list[Purchase]:
        now = datetime.now()
        prefix = now.strftime("%Y-%m")
        return [p for p in self.get_all() if p.date.startswith(prefix)]

    def get_by_supplier(self, supplier_id: int) -> list[Purchase]:
        return [p for p in self.get_all() if p.supplier_id == supplier_id]

    def create_purchase(
        self,
        supplier_id: int,
        items: list[dict],
        user: User,
        note: str = "",
    ) -> Purchase:
        if not items:
            raise ValueError("Aucun article dans l'achat.")
        supplier = self.suppliers.get_by_id(supplier_id)
        if not supplier:
            raise ValueError("Fournisseur introuvable.")

        purchase_items: list[PurchaseItem] = []
        for raw in items:
            product = self.products.get_by_id(int(raw["product_id"]))
            if not product:
                raise ValueError(f"Produit #{raw['product_id']} introuvable.")
            qty = validate_int(raw.get("quantity", 0), "Quantité", 1)
            price = validate_positive_number(
                raw.get("unit_price", product.purchase_price), "Prix d'achat"
            )
            purchase_items.append(
                PurchaseItem(
                    product_id=product.id,
                    product_code=product.code,
                    product_name=product.name,
                    quantity=qty,
                    unit_price=price,
                )
            )

        purchase = Purchase(
            id=self.storage.next_id(self.FILE),
            supplier_id=supplier.id,
            supplier_name=supplier.name,
            items=purchase_items,
            user_id=user.id,
            username=user.username,
            note=note,
        )
        purchase.recalculate()

        for item in purchase_items:
            self.stock.add_entry(
                product_id=item.product_id,
                quantity=item.quantity,
                reason="Achat fournisseur",
                user_id=user.id,
                username=user.username,
                reference=f"Achat #{purchase.id}",
            )
            # Mettre à jour le prix d'achat du produit
            self.products.update(item.product_id, purchase_price=item.unit_price)

        purchases = self._all()
        purchases.append(purchase)
        self._save(purchases)
        return purchase

    def today_total(self) -> float:
        return sum(p.total for p in self.get_today())
