from __future__ import annotations

from typing import Optional

from models.user import User
from utils.json_storage import JsonStorage
from utils.security import hash_password, verify_password
from utils.validators import require_non_empty, validate_email

class AuthService:
    FILE = "users.json"

    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage
        self._ensure_defaults()

    def _ensure_defaults(self) -> None:
        users = self.storage.load(self.FILE, default=[])
        if users:
            return
        defaults = [
            User(
                id=1,
                username="admin",
                password_hash=hash_password("admin123"),
                role="admin",
                first_name="Admin",
                last_name="StockTN",
                email="admin@stocktn.tn",
                active=True,
            ),
            User(
                id=2,
                username="vendeur",
                password_hash=hash_password("vendeur123"),
                role="seller",
                first_name="Sami",
                last_name="Ben Ali",
                email="vendeur@stocktn.tn",
                active=True,
            ),
            User(
                id=3,
                username="client",
                password_hash=hash_password("client123"),
                role="client",
                first_name="Dhia Eddine",
                last_name="Saied",
                email="dhiasaied733@gmail.com",
                phone="92021578",
                customer_id=1,
                active=True,
            ),
        ]
        self.storage.save(self.FILE, [u.to_dict() for u in defaults])

    def _all(self) -> list[User]:
        return [User.from_dict(u) for u in self.storage.load(self.FILE, default=[])]

    def _save_all(self, users: list[User]) -> None:
        self.storage.save(self.FILE, [u.to_dict() for u in users])

    def login(self, username: str, password: str) -> User:
        username = require_non_empty(username, "Nom d'utilisateur")
        password = require_non_empty(password, "Mot de passe")
        for user in self._all():
            if user.username.lower() == username.lower():
                if not user.active:
                    raise ValueError("Ce compte est désactivé.")
                if verify_password(password, user.password_hash):
                    return user
                raise ValueError("Identifiants incorrects.")
        raise ValueError("Identifiants incorrects.")

    def get_all(self) -> list[User]:
        return self._all()

    def get_by_id(self, user_id: int) -> Optional[User]:
        for user in self._all():
            if user.id == user_id:
                return user
        return None

    def create_user(
        self,
        username: str,
        password: str,
        role: str,
        first_name: str = "",
        last_name: str = "",
        email: str = "",
        phone: str = "",
        customer_id: Optional[int] = None,
    ) -> User:
        username = require_non_empty(username, "Nom d'utilisateur")
        password = require_non_empty(password, "Mot de passe")
        if role not in ("admin", "seller", "client"):
            raise ValueError("Rôle invalide.")
        if any(u.username.lower() == username.lower() for u in self._all()):
            raise ValueError("Ce nom d'utilisateur existe déjà.")
        email = validate_email(email)
        user = User(
            id=self.storage.next_id(self.FILE),
            username=username,
            password_hash=hash_password(password),
            role=role,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=email,
            phone=phone.strip(),
            customer_id=customer_id,
            active=True,
        )
        users = self._all()
        users.append(user)
        self._save_all(users)
        return user

    def update_user(self, user_id: int, **kwargs) -> User:
        users = self._all()
        for i, user in enumerate(users):
            if user.id != user_id:
                continue
            if "username" in kwargs and kwargs["username"]:
                new_name = kwargs["username"].strip()
                if any(
                    u.username.lower() == new_name.lower() and u.id != user_id
                    for u in users
                ):
                    raise ValueError("Ce nom d'utilisateur existe déjà.")
                user.username = new_name
            if "password" in kwargs and kwargs["password"]:
                user.password_hash = hash_password(kwargs["password"])
            if "role" in kwargs and kwargs["role"]:
                if kwargs["role"] not in ("admin", "seller", "client"):
                    raise ValueError("Rôle invalide.")
                user.role = kwargs["role"]
            if "first_name" in kwargs:
                user.first_name = kwargs["first_name"]
            if "last_name" in kwargs:
                user.last_name = kwargs["last_name"]
            if "email" in kwargs:
                user.email = validate_email(kwargs["email"])
            if "phone" in kwargs:
                user.phone = kwargs["phone"]
            if "active" in kwargs:
                user.active = bool(kwargs["active"])
            if "customer_id" in kwargs:
                user.customer_id = kwargs["customer_id"]
            users[i] = user
            self._save_all(users)
            return user
        raise ValueError("Utilisateur introuvable.")

    def delete_user(self, user_id: int) -> None:
        users = self._all()
        if len(users) <= 1:
            raise ValueError("Impossible de supprimer le dernier utilisateur.")
        filtered = [u for u in users if u.id != user_id]
        if len(filtered) == len(users):
            raise ValueError("Utilisateur introuvable.")
        if not any(u.role == "admin" and u.active for u in filtered):
            raise ValueError("Il doit rester au moins un administrateur actif.")
        self._save_all(filtered)
