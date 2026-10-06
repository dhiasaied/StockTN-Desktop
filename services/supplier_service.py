from __future__ import annotations

from typing import Optional

from models.supplier import Supplier
from utils.json_storage import JsonStorage
from utils.validators import require_non_empty, validate_email, validate_phone

class SupplierService:
    FILE = "suppliers.json"

    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage
        self._ensure_defaults()

    def _ensure_defaults(self) -> None:
        if self.storage.load(self.FILE, default=[]):
            return
        samples = [
            Supplier(
                1, "TechDistrib Tunisie", "71 123 456", "contact@techdistrib.tn",
                "Zone Industrielle Charguia", "Tunis", "Tunis", "1234567/A/M/000"
            ),
            Supplier(
                2, "ElectroPlus", "74 987 654", "info@electroplus.tn",
                "Route de Gabès", "Sfax", "Sfax", "7654321/B/M/000"
            ),
            Supplier(
                3, "Maison & Co", "73 555 222", "vente@maisonco.tn",
                "Av. de la République", "Sousse", "Sousse", "9988776/C/M/000"
            ),
        ]
        self.storage.save(self.FILE, [s.to_dict() for s in samples])

    def _all(self) -> list[Supplier]:
        return [
            Supplier.from_dict(s) for s in self.storage.load(self.FILE, default=[])
        ]

    def _save(self, suppliers: list[Supplier]) -> None:
        self.storage.save(self.FILE, [s.to_dict() for s in suppliers])

    def get_all(self, active_only: bool = True) -> list[Supplier]:
        suppliers = self._all()
        return [s for s in suppliers if s.active] if active_only else suppliers

    def get_by_id(self, supplier_id: int) -> Optional[Supplier]:
        for s in self._all():
            if s.id == supplier_id:
                return s
        return None

    def search(self, query: str) -> list[Supplier]:
        q = (query or "").strip().lower()
        if not q:
            return self.get_all(active_only=False)
        return [
            s
            for s in self._all()
            if q in s.name.lower()
            or q in s.city.lower()
            or q in s.phone.lower()
            or q in s.tax_id.lower()
        ]

    def create(self, **data) -> Supplier:
        name = require_non_empty(data.get("name", ""), "Nom fournisseur")
        supplier = Supplier(
            id=self.storage.next_id(self.FILE),
            name=name,
            phone=validate_phone(data.get("phone", "")),
            email=validate_email(data.get("email", "")),
            address=data.get("address", "").strip(),
            city=data.get("city", "").strip(),
            governorate=data.get("governorate", "").strip(),
            tax_id=data.get("tax_id", "").strip(),
        )
        suppliers = self._all()
        suppliers.append(supplier)
        self._save(suppliers)
        return supplier

    def update(self, supplier_id: int, **data) -> Supplier:
        suppliers = self._all()
        for i, supplier in enumerate(suppliers):
            if supplier.id != supplier_id:
                continue
            if "name" in data:
                supplier.name = require_non_empty(data["name"], "Nom fournisseur")
            if "phone" in data:
                supplier.phone = validate_phone(data["phone"])
            if "email" in data:
                supplier.email = validate_email(data["email"])
            if "address" in data:
                supplier.address = data["address"].strip()
            if "city" in data:
                supplier.city = data["city"].strip()
            if "governorate" in data:
                supplier.governorate = data["governorate"].strip()
            if "tax_id" in data:
                supplier.tax_id = data["tax_id"].strip()
            if "active" in data:
                supplier.active = bool(data["active"])
            suppliers[i] = supplier
            self._save(suppliers)
            return supplier
        raise ValueError("Fournisseur introuvable.")

    def delete(self, supplier_id: int) -> None:
        suppliers = self._all()
        filtered = [s for s in suppliers if s.id != supplier_id]
        if len(filtered) == len(suppliers):
            raise ValueError("Fournisseur introuvable.")
        self._save(filtered)
