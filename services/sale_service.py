from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from models.sale import Sale, SaleItem
from models.user import User
from services.product_service import ProductService
from services.stock_service import StockService
from utils.json_storage import JsonStorage
from utils.validators import validate_int

class SaleService:
    FILE = "sales.json"

    def __init__(
        self,
        storage: JsonStorage,
        product_service: ProductService,
        stock_service: StockService,
    ) -> None:
        self.storage = storage
        self.products = product_service
        self.stock = stock_service
        if not self.storage.path_for(self.FILE).exists():
            self.storage.save(self.FILE, [])

    def _all(self) -> list[Sale]:
        return [Sale.from_dict(s) for s in self.storage.load(self.FILE, default=[])]

    def _save(self, sales: list[Sale]) -> None:
        self.storage.save(self.FILE, [s.to_dict() for s in sales])

    def get_all(self) -> list[Sale]:
        return sorted(self._all(), key=lambda s: s.date, reverse=True)

    def get_by_id(self, sale_id: int) -> Optional[Sale]:
        for sale in self._all():
            if sale.id == sale_id:
                return sale
        return None

    def get_by_customer(self, customer_id: int) -> list[Sale]:
        return [s for s in self.get_all() if s.customer_id == customer_id]

    def get_today(self) -> list[Sale]:
        today = datetime.now().strftime("%Y-%m-%d")
        return [s for s in self.get_all() if s.date.startswith(today)]

    def get_period(self, start: datetime, end: datetime) -> list[Sale]:
        result = []
        for sale in self._all():
            try:
                d = datetime.strptime(sale.date[:19], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
            if start <= d <= end:
                result.append(sale)
        return sorted(result, key=lambda s: s.date, reverse=True)

    def get_week(self) -> list[Sale]:
        end = datetime.now()
        start = end - timedelta(days=7)
        return self.get_period(start, end)

    def get_month(self) -> list[Sale]:
        now = datetime.now()
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return self.get_period(start, now)

    def create_sale(
        self,
        items: list[dict],
        user: User,
        customer_id: Optional[int] = None,
        customer_name: str = "Client comptoir",
        payment_method: str = "Espèces",
        note: str = "",
    ) -> Sale:
        if not items:
            raise ValueError("Le panier est vide.")

        sale_items: list[SaleItem] = []
        for raw in items:
            product = self.products.get_by_id(int(raw["product_id"]))
            if not product:
                raise ValueError(f"Produit #{raw['product_id']} introuvable.")
            qty = validate_int(raw.get("quantity", 0), "Quantité", 1)
            if product.quantity < qty:
                raise ValueError(
                    f"Stock insuffisant pour {product.name} "
                    f"(disponible: {product.quantity})."
                )
            price = float(raw.get("unit_price", product.sale_price))
            sale_items.append(
                SaleItem(
                    product_id=product.id,
                    product_code=product.code,
                    product_name=product.name,
                    quantity=qty,
                    unit_price=price,
                )
            )

        sale = Sale(
            id=self.storage.next_id(self.FILE),
            items=sale_items,
            customer_id=customer_id,
            customer_name=customer_name,
            user_id=user.id,
            username=user.username,
            payment_method=payment_method,
            note=note,
        )
        sale.recalculate()

        for item in sale_items:
            self.stock.add_exit(
                product_id=item.product_id,
                quantity=item.quantity,
                reason="Vente",
                user_id=user.id,
                username=user.username,
                reference=f"Vente #{sale.id}",
            )

        sales = self._all()
        sales.append(sale)
        self._save(sales)
        return sale

    def today_total(self) -> float:
        return sum(s.total for s in self.get_today())
