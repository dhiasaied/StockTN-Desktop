from __future__ import annotations

from typing import Optional

from models.category import Category
from utils.json_storage import JsonStorage
from utils.validators import require_non_empty

class CategoryService:
    FILE = "categories.json"

    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage
        self._ensure_defaults()

    def _ensure_defaults(self) -> None:
        if self.storage.load(self.FILE, default=[]):
            return
        defaults = [
            Category(1, "Informatique", "Ordinateurs, composants et périphériques"),
            Category(2, "Téléphonie", "Smartphones et accessoires mobiles"),
            Category(3, "Électronique", "Appareils électroniques divers"),
            Category(4, "Accessoires", "Câbles, housses, chargeurs"),
            Category(5, "Maison", "Équipements pour la maison"),
            Category(6, "Bureau", "Fournitures de bureau"),
            Category(7, "Électroménager", "Appareils électroménagers"),
        ]
        self.storage.save(self.FILE, [c.to_dict() for c in defaults])

    def _all(self) -> list[Category]:
        return [Category.from_dict(c) for c in self.storage.load(self.FILE, default=[])]

    def _save(self, categories: list[Category]) -> None:
        self.storage.save(self.FILE, [c.to_dict() for c in categories])

    def get_all(self, active_only: bool = False) -> list[Category]:
        cats = self._all()
        return [c for c in cats if c.active] if active_only else cats

    def get_by_id(self, category_id: int) -> Optional[Category]:
        for cat in self._all():
            if cat.id == category_id:
                return cat
        return None

    def search(self, query: str) -> list[Category]:
        q = (query or "").strip().lower()
        if not q:
            return self.get_all()
        return [
            c
            for c in self._all()
            if q in c.name.lower() or q in c.description.lower()
        ]

    def create(self, name: str, description: str = "") -> Category:
        name = require_non_empty(name, "Nom de catégorie")
        if any(c.name.lower() == name.lower() for c in self._all()):
            raise ValueError("Cette catégorie existe déjà.")
        cat = Category(
            id=self.storage.next_id(self.FILE),
            name=name,
            description=description.strip(),
        )
        cats = self._all()
        cats.append(cat)
        self._save(cats)
        return cat

    def update(self, category_id: int, name: str, description: str = "") -> Category:
        name = require_non_empty(name, "Nom de catégorie")
        cats = self._all()
        for i, cat in enumerate(cats):
            if cat.id != category_id:
                continue
            if any(
                c.name.lower() == name.lower() and c.id != category_id for c in cats
            ):
                raise ValueError("Cette catégorie existe déjà.")
            cat.name = name
            cat.description = description.strip()
            cats[i] = cat
            self._save(cats)
            return cat
        raise ValueError("Catégorie introuvable.")

    def delete(self, category_id: int) -> None:
        cats = self._all()
        filtered = [c for c in cats if c.id != category_id]
        if len(filtered) == len(cats):
            raise ValueError("Catégorie introuvable.")
        self._save(filtered)
