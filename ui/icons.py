from __future__ import annotations

from functools import lru_cache
from typing import Optional, Tuple

from PIL import Image, ImageDraw

# Cache CTkImage instances keyed by (name, size, color)
_ctk_cache: dict[tuple, object] = {}

def _hex_to_rgb(color: str) -> Tuple[int, int, int]:
    c = color.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return tuple(int(c[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]

def _line(draw: ImageDraw.ImageDraw, pts, color, width: int) -> None:
    draw.line(pts, fill=color, width=width, joint="curve")

def _arc(draw: ImageDraw.ImageDraw, box, start, end, color, width: int) -> None:
    draw.arc(box, start=start, end=end, fill=color, width=width)

def _draw_icon(name: str, size: int, color: str) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    rgb = _hex_to_rgb(color)
    # Stroke proportionnel à la taille (style Lucide ~2px @ 24)
    w = max(2, round(size * 0.085))
    # Marges internes
    m = size * 0.18
    L, T, R, B = m, m, size - m, size - m
    cx, cy = size / 2, size / 2

    def circle(x, y, r, fill=None, outline=None):
        draw.ellipse(
            [x - r, y - r, x + r, y + r],
            fill=fill,
            outline=outline or rgb,
            width=w if outline is not False else 0,
        )

    n = name.lower().replace("_", "-")

    if n in ("layout-dashboard", "dashboard", "home"):
        gap = size * 0.06
        mid_x = cx
        mid_y = cy
        # 4 rectangles arrondis
        boxes = [
            (L, T, mid_x - gap, mid_y - gap),
            (mid_x + gap, T, R, mid_y - gap * 0.3),
            (L, mid_y + gap, mid_x - gap * 0.3, B),
            (mid_x + gap * 0.5, mid_y + gap * 0.5, R, B),
        ]
        for box in boxes:
            draw.rounded_rectangle(box, radius=size * 0.06, outline=rgb, width=w)

    elif n in ("package", "box", "products"):
        # Cube
        top = size * 0.28
        _line(draw, [(cx, T), (R, top), (cx, top * 2 - T + size * 0.08), (L, top), (cx, T)], rgb, w)
        _line(draw, [(cx, top * 2 - T + size * 0.08), (cx, B)], rgb, w)
        _line(draw, [(L, top), (L, B - size * 0.12), (cx, B)], rgb, w)
        _line(draw, [(R, top), (R, B - size * 0.12), (cx, B)], rgb, w)

    elif n in ("tags", "tag", "categories"):
        draw.rounded_rectangle(
            [L, T + size * 0.08, cx + size * 0.08, B - size * 0.08],
            radius=size * 0.08,
            outline=rgb,
            width=w,
        )
        _line(draw, [(cx + size * 0.08, T + size * 0.22), (R, cy), (cx + size * 0.08, B - size * 0.22)], rgb, w)
        circle(L + size * 0.18, T + size * 0.28, size * 0.05, fill=rgb, outline=False)

    elif n in ("warehouse", "stock", "archive"):
        _line(draw, [(L, cy - size * 0.05), (cx, T), (R, cy - size * 0.05)], rgb, w)
        _line(draw, [(L, cy - size * 0.05), (L, B), (R, B), (R, cy - size * 0.05)], rgb, w)
        _line(draw, [(cx, cy - size * 0.05), (cx, B)], rgb, w)
        _line(draw, [(L + size * 0.12, cy + size * 0.12), (cx - size * 0.08, cy + size * 0.12)], rgb, w)
        _line(draw, [(cx + size * 0.08, cy + size * 0.12), (R - size * 0.12, cy + size * 0.12)], rgb, w)

    elif n in ("shopping-cart", "cart", "sales", "caisse"):
        _line(draw, [(L, T + size * 0.08), (L + size * 0.1, T + size * 0.08),
                     (L + size * 0.22, cy + size * 0.05), (R - size * 0.08, cy + size * 0.05)], rgb, w)
        _line(draw, [(L + size * 0.22, cy + size * 0.05),
                     (L + size * 0.18, B - size * 0.22), (R - size * 0.15, B - size * 0.22)], rgb, w)
        circle(L + size * 0.28, B - size * 0.08, size * 0.07, outline=rgb)
        circle(R - size * 0.22, B - size * 0.08, size * 0.07, outline=rgb)

    elif n in ("truck", "purchases", "delivery"):
        draw.rounded_rectangle([L, cy - size * 0.12, cx + size * 0.05, B - size * 0.2], radius=2, outline=rgb, width=w)
        _line(draw, [(cx + size * 0.05, cy), (R - size * 0.05, cy), (R, cy + size * 0.12),
                     (R, B - size * 0.2), (cx + size * 0.05, B - size * 0.2)], rgb, w)
        circle(L + size * 0.18, B - size * 0.08, size * 0.08, outline=rgb)
        circle(R - size * 0.18, B - size * 0.08, size * 0.08, outline=rgb)
        _line(draw, [(L + size * 0.08, T + size * 0.15), (cx, T + size * 0.15)], rgb, w)

    elif n in ("users", "customers", "people"):
        circle(cx, T + size * 0.2, size * 0.14, outline=rgb)
        _arc(draw, [L + size * 0.05, cy - size * 0.05, R - size * 0.05, B + size * 0.15], 200, 340, rgb, w)
        # second person hint
        circle(R - size * 0.12, T + size * 0.28, size * 0.1, outline=rgb)
        _arc(draw, [cx + size * 0.05, cy + size * 0.05, R + size * 0.05, B + size * 0.1], 220, 320, rgb, w)

    elif n in ("building-2", "building", "suppliers", "company"):
        draw.rectangle([L + size * 0.05, T + size * 0.1, R - size * 0.05, B], outline=rgb, width=w)
        for i in range(3):
            y = T + size * 0.28 + i * size * 0.18
            _line(draw, [(L + size * 0.2, y), (cx - size * 0.08, y)], rgb, w)
            _line(draw, [(cx + size * 0.08, y), (R - size * 0.2, y)], rgb, w)
        draw.rectangle([cx - size * 0.1, B - size * 0.22, cx + size * 0.1, B], outline=rgb, width=w)

    elif n in ("clipboard-list", "orders", "clipboard"):
        draw.rounded_rectangle([L + size * 0.08, T + size * 0.18, R - size * 0.08, B], radius=size * 0.06, outline=rgb, width=w)
        draw.rounded_rectangle([cx - size * 0.18, T, cx + size * 0.18, T + size * 0.22], radius=size * 0.04, outline=rgb, width=w)
        for i in range(3):
            y = T + size * 0.4 + i * size * 0.16
            _line(draw, [(L + size * 0.25, y), (R - size * 0.25, y)], rgb, w)

    elif n in ("user-cog", "user", "users-admin", "profile"):
        circle(cx, T + size * 0.22, size * 0.16, outline=rgb)
        _arc(draw, [L + size * 0.08, cy, R - size * 0.08, B + size * 0.2], 200, 340, rgb, w)

    elif n in ("bar-chart-3", "chart", "reports", "analytics"):
        _line(draw, [(L, B), (R, B)], rgb, w)
        bars = [
            (L + size * 0.08, cy + size * 0.1, L + size * 0.22, B),
            (cx - size * 0.08, T + size * 0.15, cx + size * 0.08, B),
            (R - size * 0.22, cy - size * 0.05, R - size * 0.08, B),
        ]
        for box in bars:
            draw.rectangle(box, outline=rgb, width=w)

    elif n in ("database-backup", "database", "settings", "backup", "hard-drive"):
        _arc(draw, [L, T, R, T + size * 0.35], 0, 360, rgb, w)
        _line(draw, [(L, T + size * 0.18), (L, B - size * 0.18)], rgb, w)
        _line(draw, [(R, T + size * 0.18), (R, B - size * 0.18)], rgb, w)
        _arc(draw, [L, B - size * 0.35, R, B], 0, 180, rgb, w)
        _arc(draw, [L, cy - size * 0.1, R, cy + size * 0.25], 0, 180, rgb, w)

    elif n in ("log-out", "logout", "exit"):
        draw.rounded_rectangle([L, T + size * 0.08, cx + size * 0.05, B - size * 0.08], radius=size * 0.06, outline=rgb, width=w)
        _line(draw, [(cx - size * 0.05, cy), (R, cy)], rgb, w)
        _line(draw, [(R - size * 0.18, cy - size * 0.14), (R, cy), (R - size * 0.18, cy + size * 0.14)], rgb, w)

    elif n in ("plus", "add"):
        _line(draw, [(cx, T + size * 0.1), (cx, B - size * 0.1)], rgb, w)
        _line(draw, [(L + size * 0.1, cy), (R - size * 0.1, cy)], rgb, w)

    elif n in ("pencil", "edit", "modify"):
        _line(draw, [(L + size * 0.1, B - size * 0.15), (R - size * 0.25, T + size * 0.2)], rgb, w)
        _line(draw, [(R - size * 0.25, T + size * 0.2), (R - size * 0.1, T + size * 0.35),
                     (L + size * 0.25, B - size * 0.02), (L + size * 0.1, B - size * 0.15)], rgb, w)
        _line(draw, [(L + size * 0.08, B - size * 0.08), (L + size * 0.28, B - size * 0.02)], rgb, w)

    elif n in ("trash-2", "trash", "delete"):
        _line(draw, [(L + size * 0.08, T + size * 0.22), (R - size * 0.08, T + size * 0.22)], rgb, w)
        _line(draw, [(cx - size * 0.12, T + size * 0.08), (cx + size * 0.12, T + size * 0.08)], rgb, w)
        draw.rounded_rectangle(
            [L + size * 0.15, T + size * 0.22, R - size * 0.15, B],
            radius=size * 0.04,
            outline=rgb,
            width=w,
        )
        _line(draw, [(cx, T + size * 0.35), (cx, B - size * 0.12)], rgb, w)
        _line(draw, [(cx - size * 0.14, T + size * 0.35), (cx - size * 0.14, B - size * 0.12)], rgb, w)
        _line(draw, [(cx + size * 0.14, T + size * 0.35), (cx + size * 0.14, B - size * 0.12)], rgb, w)

    elif n in ("refresh-cw", "refresh", "reload"):
        _arc(draw, [L + size * 0.08, T + size * 0.08, R - size * 0.08, B - size * 0.08], 40, 290, rgb, w)
        _line(draw, [(R - size * 0.08, T + size * 0.2), (R - size * 0.08, T + size * 0.42),
                     (R - size * 0.28, T + size * 0.42)], rgb, w)

    elif n in ("search", "magnifier"):
        circle(cx - size * 0.08, cy - size * 0.08, size * 0.22, outline=rgb)
        _line(draw, [(cx + size * 0.1, cy + size * 0.1), (R - size * 0.05, B - size * 0.05)], rgb, w)

    elif n in ("bell", "notification", "alert"):
        _arc(draw, [L + size * 0.12, T + size * 0.12, R - size * 0.12, cy + size * 0.2], 180, 360, rgb, w)
        _line(draw, [(L + size * 0.12, cy), (L + size * 0.12, cy + size * 0.15),
                     (R - size * 0.12, cy + size * 0.15), (R - size * 0.12, cy)], rgb, w)
        _line(draw, [(L + size * 0.05, cy + size * 0.15), (R - size * 0.05, cy + size * 0.15)], rgb, w)
        _arc(draw, [cx - size * 0.1, B - size * 0.22, cx + size * 0.1, B - size * 0.02], 0, 180, rgb, w)

    elif n in ("check", "success", "check-circle"):
        if "circle" in n:
            circle(cx, cy, size * 0.38, outline=rgb)
        _line(draw, [(L + size * 0.18, cy), (cx - size * 0.05, B - size * 0.22),
                     (R - size * 0.15, T + size * 0.22)], rgb, w)

    elif n in ("x", "error", "x-circle", "close"):
        if "circle" in n:
            circle(cx, cy, size * 0.38, outline=rgb)
        _line(draw, [(L + size * 0.22, T + size * 0.22), (R - size * 0.22, B - size * 0.22)], rgb, w)
        _line(draw, [(R - size * 0.22, T + size * 0.22), (L + size * 0.22, B - size * 0.22)], rgb, w)

    elif n in ("alert-triangle", "warning"):
        _line(draw, [(cx, T + size * 0.08), (R - size * 0.05, B - size * 0.08),
                     (L + size * 0.05, B - size * 0.08), (cx, T + size * 0.08)], rgb, w)
        _line(draw, [(cx, T + size * 0.35), (cx, cy + size * 0.08)], rgb, w)
        circle(cx, B - size * 0.22, size * 0.04, fill=rgb, outline=False)

    elif n in ("inbox", "empty", "folder-open"):
        _line(draw, [(L, cy), (L + size * 0.15, T + size * 0.15), (R - size * 0.15, T + size * 0.15), (R, cy)], rgb, w)
        draw.rounded_rectangle([L, cy, R, B], radius=size * 0.06, outline=rgb, width=w)
        _line(draw, [(L, cy), (cx - size * 0.12, cy + size * 0.15), (cx + size * 0.12, cy + size * 0.15), (R, cy)], rgb, w)

    elif n in ("loader", "loading", "spinner"):
        _arc(draw, [L + size * 0.1, T + size * 0.1, R - size * 0.1, B - size * 0.1], -60, 200, rgb, w)

    elif n in ("trending-up", "trend"):
        _line(draw, [(L, B - size * 0.15), (cx - size * 0.05, cy + size * 0.05),
                     (cx + size * 0.1, cy - size * 0.1), (R - size * 0.05, T + size * 0.2)], rgb, w)
        _line(draw, [(R - size * 0.28, T + size * 0.2), (R - size * 0.05, T + size * 0.2),
                     (R - size * 0.05, T + size * 0.45)], rgb, w)

    elif n in ("trending-down",):
        _line(draw, [(L, T + size * 0.2), (cx - size * 0.05, cy - size * 0.05),
                     (cx + size * 0.1, cy + size * 0.1), (R - size * 0.05, B - size * 0.2)], rgb, w)

    elif n in ("shopping-bag", "order-product"):
        draw.rounded_rectangle([L + size * 0.08, T + size * 0.28, R - size * 0.08, B], radius=size * 0.06, outline=rgb, width=w)
        _arc(draw, [L + size * 0.22, T + size * 0.05, R - size * 0.22, cy + size * 0.05], 180, 360, rgb, w)

    elif n in ("file-text", "file", "export"):
        _line(draw, [(L + size * 0.12, T + size * 0.08), (cx + size * 0.05, T + size * 0.08),
                     (R - size * 0.08, T + size * 0.28), (R - size * 0.08, B - size * 0.08),
                     (L + size * 0.12, B - size * 0.08), (L + size * 0.12, T + size * 0.08)], rgb, w)
        _line(draw, [(cx + size * 0.05, T + size * 0.08), (cx + size * 0.05, T + size * 0.28),
                     (R - size * 0.08, T + size * 0.28)], rgb, w)
        for i in range(3):
            y = cy - size * 0.05 + i * size * 0.14
            _line(draw, [(L + size * 0.25, y), (R - size * 0.22, y)], rgb, w)

    elif n in ("download", "import"):
        _line(draw, [(cx, T + size * 0.08), (cx, B - size * 0.28)], rgb, w)
        _line(draw, [(cx - size * 0.16, cy), (cx, B - size * 0.28), (cx + size * 0.16, cy)], rgb, w)
        _line(draw, [(L + size * 0.1, B - size * 0.18), (L + size * 0.1, B - size * 0.08),
                     (R - size * 0.1, B - size * 0.08), (R - size * 0.1, B - size * 0.18)], rgb, w)

    elif n in ("upload",):
        _line(draw, [(cx, B - size * 0.28), (cx, T + size * 0.08)], rgb, w)
        _line(draw, [(cx - size * 0.16, T + size * 0.28), (cx, T + size * 0.08), (cx + size * 0.16, T + size * 0.28)], rgb, w)
        _line(draw, [(L + size * 0.1, B - size * 0.18), (L + size * 0.1, B - size * 0.08),
                     (R - size * 0.1, B - size * 0.08), (R - size * 0.1, B - size * 0.18)], rgb, w)

    elif n in ("eye", "preview"):
        _arc(draw, [L, cy - size * 0.25, R, cy + size * 0.25], 20, 160, rgb, w)
        _arc(draw, [L, cy - size * 0.25, R, cy + size * 0.25], 200, 340, rgb, w)
        circle(cx, cy, size * 0.12, outline=rgb)

    elif n in ("lock", "password"):
        draw.rounded_rectangle([L + size * 0.12, cy - size * 0.05, R - size * 0.12, B], radius=size * 0.06, outline=rgb, width=w)
        _arc(draw, [L + size * 0.22, T + size * 0.05, R - size * 0.22, cy + size * 0.1], 180, 360, rgb, w)
        circle(cx, cy + size * 0.12, size * 0.05, fill=rgb, outline=False)

    elif n in ("mail", "email"):
        draw.rounded_rectangle([L, T + size * 0.18, R, B - size * 0.12], radius=size * 0.05, outline=rgb, width=w)
        _line(draw, [(L, T + size * 0.22), (cx, cy + size * 0.05), (R, T + size * 0.22)], rgb, w)

    elif n in ("phone",):
        draw.rounded_rectangle([L + size * 0.22, T + size * 0.05, R - size * 0.22, B - size * 0.05], radius=size * 0.1, outline=rgb, width=w)
        _line(draw, [(cx - size * 0.08, B - size * 0.18), (cx + size * 0.08, B - size * 0.18)], rgb, w)

    elif n in ("map-pin", "location"):
        _arc(draw, [L + size * 0.12, T + size * 0.05, R - size * 0.12, cy + size * 0.25], 0, 360, rgb, w)
        _line(draw, [(L + size * 0.12, cy), (cx, B - size * 0.05), (R - size * 0.12, cy)], rgb, w)
        circle(cx, cy - size * 0.08, size * 0.08, outline=rgb)

    elif n in ("calendar",):
        draw.rounded_rectangle([L, T + size * 0.15, R, B], radius=size * 0.06, outline=rgb, width=w)
        _line(draw, [(L, T + size * 0.35), (R, T + size * 0.35)], rgb, w)
        _line(draw, [(L + size * 0.22, T + size * 0.05), (L + size * 0.22, T + size * 0.25)], rgb, w)
        _line(draw, [(R - size * 0.22, T + size * 0.05), (R - size * 0.22, T + size * 0.25)], rgb, w)

    elif n in ("zap", "quick"):
        _line(draw, [(cx + size * 0.08, T), (L + size * 0.15, cy + size * 0.05),
                     (cx, cy + size * 0.05), (cx - size * 0.08, B),
                     (R - size * 0.15, cy - size * 0.05), (cx, cy - size * 0.05),
                     (cx + size * 0.08, T)], rgb, w)

    elif n in ("layers",):
        _line(draw, [(cx, T), (R, T + size * 0.2), (cx, T + size * 0.4), (L, T + size * 0.2), (cx, T)], rgb, w)
        _line(draw, [(L, cy), (cx, cy + size * 0.2), (R, cy), (cx, B), (L, cy)], rgb, max(1, w - 1))

    else:
        # fallback: cercle simple
        circle(cx, cy, size * 0.3, outline=rgb)

    return img

def get_pil_icon(name: str, size: int = 20, color: str = "#FFFFFF") -> Image.Image:
    return _draw_icon(name, size, color)

def get_icon(name: str, size: int = 20, color: str = "#FFFFFF"):
    import customtkinter as ctk

    key = (name, size, color.lower())
    if key in _ctk_cache:
        return _ctk_cache[key]
    pil = get_pil_icon(name, size, color)
    img = ctk.CTkImage(light_image=pil, dark_image=pil, size=(size, size))
    _ctk_cache[key] = img
    return img

# Mapping menu / actions → nom d'icône
NAV_ICONS = {
    "dashboard": "layout-dashboard",
    "products": "package",
    "categories": "tags",
    "stock": "warehouse",
    "sales": "shopping-cart",
    "purchases": "truck",
    "customers": "users",
    "suppliers": "building-2",
    "orders": "clipboard-list",
    "users": "user-cog",
    "reports": "bar-chart-3",
    "settings": "database-backup",
    "profile": "user",
}

ACTION_ICONS = {
    "add": "plus",
    "edit": "pencil",
    "delete": "trash-2",
    "refresh": "refresh-cw",
    "search": "search",
    "logout": "log-out",
    "order": "shopping-bag",
    "export": "file-text",
    "download": "download",
    "upload": "upload",
    "success": "check-circle",
    "error": "x-circle",
    "warning": "alert-triangle",
    "empty": "inbox",
    "loading": "loader",
    "bell": "bell",
    "trend": "trending-up",
}
