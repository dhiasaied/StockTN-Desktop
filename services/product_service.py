from __future__ import annotations

from typing import Optional

from models.product import Product
from utils.json_storage import JsonStorage
from utils.validators import (
    require_non_empty,
    validate_int,
    validate_positive_number,
)

class ProductService:
    FILE = "products.json"

    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage
        self._ensure_defaults()

    def _ensure_defaults(self) -> None:
        if self.storage.load(self.FILE, default=[]):
            return
        samples = [
            Product(1, "PRD-001", "6191501000011", "Clavier mécanique RGB", 1, "Logitech", 120.0, 179.0, 15, 5, "unité", "Clavier mécanique switch blue, rétroéclairage RGB", "prd001_keyboard.jpg"),
            Product(2, "PRD-002", "6191501000028", "Souris sans fil Pro", 1, "Logitech", 45.0, 79.0, 30, 8, "unité", "Souris ergonomique sans fil, autonomie longue durée", "prd002_mouse.jpg"),
            Product(3, "PRD-003", "6191501000035", "Moniteur LED 27 pouces", 1, "Samsung", 420.0, 549.0, 10, 3, "unité", "Écran Full HD 27\", HDMI et DisplayPort", "prd003_monitor.jpg"),
            Product(4, "PRD-004", "6191501000042", "Chargeur USB-C 65W", 4, "Anker", 35.0, 59.0, 49, 15, "unité", "Charge rapide USB-C GaN 65W", "prd004_charger.jpg"),
            Product(5, "PRD-005", "6191501000059", "Écouteurs Bluetooth Sony", 4, "Sony", 95.0, 149.0, 40, 10, "unité", "Autonomie 30h, réduction de bruit", "prd005_headphones.jpg"),
            Product(6, "PRD-006", "6191501000066", "Câble HDMI 2.1 2m", 4, "Belkin", 12.0, 29.0, 60, 20, "unité", "Câble HDMI 2.1 Ultra HD 8K, 2 mètres", "prd006_hdmi.jpg"),
            Product(7, "PRD-007", "6191501000073", "Smartphone Samsung A54", 2, "Samsung", 890.0, 1099.0, 25, 5, "unité", "128 Go, 5G", ""),
            Product(8, "PRD-008", "6191501000080", "TV LED 43 pouces", 3, "LG", 780.0, 999.0, 6, 2, "unité", "Smart TV", ""),
        ]
        self.storage.save(self.FILE, [p.to_dict() for p in samples])

    def _all(self) -> list[Product]:
        return [Product.from_dict(p) for p in self.storage.load(self.FILE, default=[])]

    def _save(self, products: list[Product]) -> None:
        self.storage.save(self.FILE, [p.to_dict() for p in products])

    def get_all(self, active_only: bool = True) -> list[Product]:
        products = self._all()
        return [p for p in products if p.active] if active_only else products

    def get_by_id(self, product_id: int) -> Optional[Product]:
        for p in self._all():
            if p.id == product_id:
                return p
        return None

    def search(
        self,
        query: str = "",
        category_id: Optional[int] = None,
        brand: str = "",
        availability: str = "all",
    ) -> list[Product]:
        q = (query or "").strip().lower()
        brand_q = (brand or "").strip().lower()
        results = self.get_all()

        if q:
            results = [
                p
                for p in results
                if q in p.code.lower()
                or q in p.name.lower()
                or q in p.barcode.lower()
                or q in p.brand.lower()
            ]
        if category_id:
            results = [p for p in results if p.category_id == category_id]
        if brand_q:
            results = [p for p in results if brand_q in p.brand.lower()]
        if availability == "available":
            results = [p for p in results if p.quantity > 0]
        elif availability == "low":
            results = [p for p in results if p.is_low_stock]
        elif availability == "out":
            results = [p for p in results if p.is_out_of_stock]
        return results

    def get_low_stock(self) -> list[Product]:
        return [p for p in self.get_all() if p.is_low_stock]

    def get_out_of_stock(self) -> list[Product]:
        return [p for p in self.get_all() if p.is_out_of_stock]

    def create(self, **data) -> Product:
        code = require_non_empty(data.get("code", ""), "Code produit")
        name = require_non_empty(data.get("name", ""), "Désignation")
        products = self._all()
        if any(p.code.lower() == code.lower() for p in products):
            raise ValueError("Ce code produit existe déjà.")
        product = Product(
            id=self.storage.next_id(self.FILE),
            code=code,
            barcode=data.get("barcode", "").strip(),
            name=name,
            category_id=validate_int(data.get("category_id", 0), "Catégorie", 1),
            brand=data.get("brand", "").strip(),
            purchase_price=validate_positive_number(
                data.get("purchase_price", 0), "Prix d'achat"
            ),
            sale_price=validate_positive_number(
                data.get("sale_price", 0), "Prix de vente", allow_zero=False
            ),
            quantity=validate_int(data.get("quantity", 0), "Quantité", 0),
            min_stock=validate_int(data.get("min_stock", 0), "Stock minimum", 0),
            unit=data.get("unit", "unité") or "unité",
            description=data.get("description", ""),
            image=data.get("image", ""),
        )
        products.append(product)
        self._save(products)
        return product

    def update(self, product_id: int, **data) -> Product:
        products = self._all()
        for i, product in enumerate(products):
            if product.id != product_id:
                continue
            if "code" in data and data["code"]:
                code = data["code"].strip()
                if any(p.code.lower() == code.lower() and p.id != product_id for p in products):
                    raise ValueError("Ce code produit existe déjà.")
                product.code = code
            if "name" in data:
                product.name = require_non_empty(data["name"], "Désignation")
            if "barcode" in data:
                product.barcode = data["barcode"].strip()
            if "category_id" in data:
                product.category_id = validate_int(data["category_id"], "Catégorie", 1)
            if "brand" in data:
                product.brand = data["brand"].strip()
            if "purchase_price" in data:
                product.purchase_price = validate_positive_number(
                    data["purchase_price"], "Prix d'achat"
                )
            if "sale_price" in data:
                product.sale_price = validate_positive_number(
                    data["sale_price"], "Prix de vente", allow_zero=False
                )
            if "quantity" in data:
                product.quantity = validate_int(data["quantity"], "Quantité", 0)
            if "min_stock" in data:
                product.min_stock = validate_int(data["min_stock"], "Stock minimum", 0)
            if "unit" in data:
                product.unit = data["unit"] or "unité"
            if "description" in data:
                product.description = data["description"]
            if "image" in data:
                product.image = data["image"]
            if "active" in data:
                product.active = bool(data["active"])
            products[i] = product
            self._save(products)
            return product
        raise ValueError("Produit introuvable.")

    def delete(self, product_id: int) -> None:
        products = self._all()
        filtered = [p for p in products if p.id != product_id]
        if len(filtered) == len(products):
            raise ValueError("Produit introuvable.")
        self._save(filtered)

    def adjust_quantity(self, product_id: int, delta: int) -> Product:
        products = self._all()
        for i, product in enumerate(products):
            if product.id != product_id:
                continue
            new_qty = product.quantity + delta
            if new_qty < 0:
                raise ValueError(
                    f"Stock insuffisant pour {product.name} (disponible: {product.quantity})."
                )
            product.quantity = new_qty
            products[i] = product
            self._save(products)
            return product
        raise ValueError("Produit introuvable.")
