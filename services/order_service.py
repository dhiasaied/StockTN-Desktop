from __future__ import annotations

from datetime import datetime
from typing import Optional

from models.order import ORDER_STATUSES, Order, OrderItem
from services.customer_service import CustomerService
from services.product_service import ProductService
from utils.json_storage import JsonStorage
from utils.validators import validate_int

class OrderService:
    FILE = "orders.json"

    def __init__(
        self,
        storage: JsonStorage,
        product_service: ProductService,
        customer_service: CustomerService,
    ) -> None:
        self.storage = storage
        self.products = product_service
        self.customers = customer_service
        if not self.storage.path_for(self.FILE).exists():
            self.storage.save(self.FILE, [])

    def _all(self) -> list[Order]:
        return [Order.from_dict(o) for o in self.storage.load(self.FILE, default=[])]

    def _save(self, orders: list[Order]) -> None:
        self.storage.save(self.FILE, [o.to_dict() for o in orders])

    def get_all(self) -> list[Order]:
        return sorted(self._all(), key=lambda o: o.date, reverse=True)

    def get_by_id(self, order_id: int) -> Optional[Order]:
        for order in self._all():
            if order.id == order_id:
                return order
        return None

    def get_by_customer(self, customer_id: int) -> list[Order]:
        return [o for o in self.get_all() if o.customer_id == customer_id]

    def create_order(
        self,
        customer_id: int,
        items: list[dict],
        note: str = "",
    ) -> Order:
        if not items:
            raise ValueError("La commande est vide.")
        customer = self.customers.get_by_id(customer_id)
        if not customer:
            raise ValueError("Client introuvable.")

        order_items: list[OrderItem] = []
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
            order_items.append(
                OrderItem(
                    product_id=product.id,
                    product_code=product.code,
                    product_name=product.name,
                    quantity=qty,
                    unit_price=product.sale_price,
                )
            )

        order = Order(
            id=self.storage.next_id(self.FILE),
            customer_id=customer.id,
            customer_name=customer.full_name,
            items=order_items,
            status="En attente",
            note=note,
        )
        order.recalculate()
        orders = self._all()
        orders.append(order)
        self._save(orders)
        return order

    def update_status(self, order_id: int, status: str) -> Order:
        if status not in ORDER_STATUSES:
            raise ValueError("Statut de commande invalide.")
        orders = self._all()
        for i, order in enumerate(orders):
            if order.id != order_id:
                continue
            order.status = status
            order.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            orders[i] = order
            self._save(orders)
            return order
        raise ValueError("Commande introuvable.")
