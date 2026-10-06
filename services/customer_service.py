from __future__ import annotations

from typing import Optional

from models.customer import Customer
from utils.json_storage import JsonStorage
from utils.validators import require_non_empty, validate_email, validate_phone

class CustomerService:
    FILE = "customers.json"

    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage
        self._ensure_defaults()

    def _ensure_defaults(self) -> None:
        if self.storage.load(self.FILE, default=[]):
            return
        samples = [
            Customer(
                1, "Saied", "Dhia Eddine", "92021578", "dhiasaied733@gmail.com",
                "Nabeul", "Tunisia", user_id=3
            ),
            Customer(
                2, "Gharbi", "Karim", "22 456 789", "karim@email.tn",
                "45 Av. Habib Bourguiba", "Sfax"
            ),
            Customer(
                3, "Jebali", "Sarra", "55 987 321", "sarra@email.tn",
                "8 Rue Ibn Khaldoun", "Sousse"
            ),
        ]
        self.storage.save(self.FILE, [c.to_dict() for c in samples])

    def _all(self) -> list[Customer]:
        return [
            Customer.from_dict(c) for c in self.storage.load(self.FILE, default=[])
        ]

    def _save(self, customers: list[Customer]) -> None:
        self.storage.save(self.FILE, [c.to_dict() for c in customers])

    def get_all(self) -> list[Customer]:
        return self._all()

    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        for c in self._all():
            if c.id == customer_id:
                return c
        return None

    def search(self, query: str) -> list[Customer]:
        q = (query or "").strip().lower()
        if not q:
            return self.get_all()
        return [
            c
            for c in self._all()
            if q in c.full_name.lower()
            or q in c.phone.lower()
            or q in c.email.lower()
            or q in c.city.lower()
        ]

    def create(self, **data) -> Customer:
        last_name = require_non_empty(data.get("last_name", ""), "Nom")
        first_name = require_non_empty(data.get("first_name", ""), "Prénom")
        customer = Customer(
            id=self.storage.next_id(self.FILE),
            last_name=last_name,
            first_name=first_name,
            phone=validate_phone(data.get("phone", "")),
            email=validate_email(data.get("email", "")),
            address=data.get("address", "").strip(),
            city=data.get("city", "").strip(),
            user_id=data.get("user_id"),
        )
        customers = self._all()
        customers.append(customer)
        self._save(customers)
        return customer

    def update(self, customer_id: int, **data) -> Customer:
        customers = self._all()
        for i, customer in enumerate(customers):
            if customer.id != customer_id:
                continue
            if "last_name" in data:
                customer.last_name = require_non_empty(data["last_name"], "Nom")
            if "first_name" in data:
                customer.first_name = require_non_empty(data["first_name"], "Prénom")
            if "phone" in data:
                customer.phone = validate_phone(data["phone"])
            if "email" in data:
                customer.email = validate_email(data["email"])
            if "address" in data:
                customer.address = data["address"].strip()
            if "city" in data:
                customer.city = data["city"].strip()
            if "user_id" in data:
                customer.user_id = data["user_id"]
            customers[i] = customer
            self._save(customers)
            return customer
        raise ValueError("Client introuvable.")

    def delete(self, customer_id: int) -> None:
        customers = self._all()
        filtered = [c for c in customers if c.id != customer_id]
        if len(filtered) == len(customers):
            raise ValueError("Client introuvable.")
        self._save(filtered)
