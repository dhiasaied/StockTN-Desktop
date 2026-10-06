from __future__ import annotations

import base64
import hashlib
import secrets

_ITERATIONS = 100_000
_SALT_SIZE = 16

def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Le mot de passe ne peut pas être vide.")
    salt = secrets.token_bytes(_SALT_SIZE)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, _ITERATIONS
    )
    return base64.b64encode(salt + digest).decode("ascii")

def verify_password(password: str, password_hash: str) -> bool:
    try:
        raw = base64.b64decode(password_hash.encode("ascii"))
        salt, stored = raw[:_SALT_SIZE], raw[_SALT_SIZE:]
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, _ITERATIONS
        )
        return secrets.compare_digest(digest, stored)
    except Exception:
        return False
