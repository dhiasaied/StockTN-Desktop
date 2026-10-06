from __future__ import annotations

import re
from typing import Optional

def require_non_empty(value: str, field: str = "Champ") -> str:
    text = (value or "").strip()
    if not text:
        raise ValueError(f"{field} est obligatoire.")
    return text

def validate_email(email: str, required: bool = False) -> str:
    email = (email or "").strip()
    if not email:
        if required:
            raise ValueError("L'email est obligatoire.")
        return ""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        raise ValueError("Adresse email invalide.")
    return email

def validate_phone(phone: str, required: bool = False) -> str:
    phone = (phone or "").strip()
    if not phone:
        if required:
            raise ValueError("Le téléphone est obligatoire.")
        return ""
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 8:
        raise ValueError("Numéro de téléphone invalide.")
    return phone

def validate_positive_number(
    value, field: str = "Valeur", allow_zero: bool = True
) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} doit être un nombre.")
    if allow_zero and number < 0:
        raise ValueError(f"{field} ne peut pas être négatif.")
    if not allow_zero and number <= 0:
        raise ValueError(f"{field} doit être supérieur à 0.")
    return number

def validate_int(
    value, field: str = "Valeur", min_value: Optional[int] = None
) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} doit être un entier.")
    if min_value is not None and number < min_value:
        raise ValueError(f"{field} doit être >= {min_value}.")
    return number

def format_tnd(amount: float) -> str:
    return f"{amount:,.3f} TND".replace(",", " ")
