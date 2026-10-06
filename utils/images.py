from __future__ import annotations

from pathlib import Path
from typing import Optional

from PIL import Image

# Dossier assets du projet (StockTN/assets)
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"

def resolve_image(image_name: str | None) -> Optional[Path]:
    if not image_name:
        return None
    path = Path(image_name)
    if not path.is_absolute():
        path = ASSETS_DIR / image_name
    if path.exists() and path.is_file():
        return path
    # Essai depuis le dossier images parent (python_json/images)
    alt = ASSETS_DIR.parent.parent / "images" / Path(image_name).name
    if alt.exists():
        return alt
    return None

def load_ctk_image(image_name: str | None, size: tuple[int, int]):
    import customtkinter as ctk

    path = resolve_image(image_name)
    if not path:
        return None
    try:
        img = Image.open(path)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    except Exception:
        return None

def load_logo(size: tuple[int, int] = (160, 160)):
    return load_ctk_image("logo.png", size)

def list_product_images() -> list[str]:
    if not ASSETS_DIR.exists():
        return []
    exts = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
    return sorted(
        p.name
        for p in ASSETS_DIR.iterdir()
        if p.suffix.lower() in exts and p.name.lower() != "logo.png"
    )
