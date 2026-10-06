COLORS = {
    # Brand
    "primary": "#0F766E",
    "primary_dark": "#0D5C56",
    "primary_light": "#14B8A6",
    "primary_soft": "#CCFBF1",
    "accent": "#E11D48",
    "accent_hover": "#BE123C",
    # Semantic
    "warning": "#D97706",
    "warning_soft": "#FEF3C7",
    "success": "#059669",
    "success_soft": "#D1FAE5",
    "danger": "#DC2626",
    "danger_soft": "#FEE2E2",
    "info": "#0284C7",
    "info_soft": "#E0F2FE",
    # Surfaces
    "bg": "#F1F5F9",
    "bg_alt": "#E8EEF4",
    "surface": "#FFFFFF",
    "surface_elevated": "#FFFFFF",
    "surface_hover": "#F8FAFC",
    # Sidebar
    "sidebar": "#0F172A",
    "sidebar_hover": "#1E293B",
    "sidebar_active": "#0F766E",
    "sidebar_text": "#94A3B8",
    "sidebar_text_active": "#FFFFFF",
    "sidebar_border": "#1E293B",
    # Text
    "text": "#0F172A",
    "text_secondary": "#334155",
    "text_muted": "#64748B",
    "text_inverse": "#FFFFFF",
    # Borders & misc
    "border": "#E2E8F0",
    "border_strong": "#CBD5E1",
    "low_stock": "#D97706",
    "out_stock": "#DC2626",
    "overlay": "#0F172A",
    "shadow": "#0F172A14",
    "input_bg": "#F8FAFC",
    "input_focus": "#0F766E",
    "chart": "#0F766E",
    "chart_alt": "#14B8A6",
}

# Rayons / espacements cohérents
RADIUS = {
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 20,
}

SPACING = {
    "page_x": 28,
    "page_y": 22,
    "section": 16,
    "card": 14,
}

FONT_FAMILY = "Segoe UI"

ROLE_LABELS = {
    "admin": "Administrateur",
    "seller": "Vendeur",
    "client": "Client",
}

# Menus par rôle : (clé, libellé)
MENUS = {
    "admin": [
        ("dashboard", "Tableau de bord"),
        ("products", "Produits"),
        ("categories", "Catégories"),
        ("stock", "Stock"),
        ("sales", "Caisse / Ventes"),
        ("purchases", "Achats"),
        ("customers", "Clients"),
        ("suppliers", "Fournisseurs"),
        ("orders", "Commandes"),
        ("users", "Utilisateurs"),
        ("reports", "Rapports"),
        ("settings", "Sauvegarde"),
    ],
    "seller": [
        ("dashboard", "Tableau de bord"),
        ("products", "Produits"),
        ("sales", "Caisse / Ventes"),
        ("customers", "Clients"),
        ("orders", "Commandes"),
    ],
    "client": [
        ("dashboard", "Tableau de bord"),
        ("products", "Catalogue"),
        ("orders", "Mes commandes"),
        ("profile", "Mon profil"),
    ],
}
