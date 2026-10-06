from __future__ import annotations

import customtkinter as ctk

from models.user import User
from services.app_context import AppContext
from ui import COLORS, FONT_FAMILY, MENUS, RADIUS, ROLE_LABELS
from ui.categories import CategoriesView
from ui.customers import CustomersView
from ui.dashboard import DashboardView
from ui.icons import NAV_ICONS, get_icon
from ui.orders import OrdersView
from ui.products import ProductsView
from ui.profile import ProfileView
from ui.purchases import PurchasesView
from ui.reports import ReportsView
from ui.sales import SalesView
from ui.settings import SettingsView
from ui.stock import StockView
from ui.suppliers import SuppliersView
from ui.users import UsersView
from utils.images import load_logo

class MainWindow(ctk.CTkFrame):
    def __init__(self, master, ctx: AppContext, user: User, on_logout):
        super().__init__(master, fg_color=COLORS["bg"])
        self.ctx = ctx
        self.user = user
        self.on_logout = on_logout
        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        self._nav_icons: dict[str, object] = {}
        self._current_key = None
        self._build()
        self.navigate("dashboard")

    def _build(self) -> None:
        self.sidebar = ctk.CTkFrame(
            self, fg_color=COLORS["sidebar"], width=248, corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Brand
        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=18, pady=(22, 6))
        logo = load_logo((56, 56))
        if logo:
            ctk.CTkLabel(brand, text="", image=logo).pack(anchor="w", pady=(0, 10))
            self._logo_ref = logo
        ctk.CTkLabel(
            brand,
            text="StockTN",
            font=ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold"),
            text_color="white",
        ).pack(anchor="w")
        ctk.CTkLabel(
            brand,
            text="Gestion professionnelle",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLORS["primary_light"],
        ).pack(anchor="w", pady=(0, 4))

        # Séparateur
        ctk.CTkFrame(self.sidebar, fg_color=COLORS["sidebar_border"], height=1).pack(
            fill="x", padx=16, pady=(8, 12)
        )

        # User card
        user_box = ctk.CTkFrame(
            self.sidebar,
            fg_color=COLORS["sidebar_hover"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["sidebar_border"],
        )
        user_box.pack(fill="x", padx=12, pady=(0, 14))

        urow = ctk.CTkFrame(user_box, fg_color="transparent")
        urow.pack(fill="x", padx=12, pady=12)
        avatar = ctk.CTkFrame(
            urow,
            fg_color=COLORS["primary"],
            width=36,
            height=36,
            corner_radius=18,
        )
        avatar.pack(side="left", padx=(0, 10))
        avatar.pack_propagate(False)
        initials = "".join(p[0] for p in self.user.full_name.split()[:2]).upper() or "?"
        ctk.CTkLabel(
            avatar,
            text=initials,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color="white",
        ).place(relx=0.5, rely=0.5, anchor="center")

        utext = ctk.CTkFrame(urow, fg_color="transparent")
        utext.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            utext,
            text=self.user.full_name,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color="white",
            anchor="w",
        ).pack(fill="x")
        ctk.CTkLabel(
            utext,
            text=ROLE_LABELS.get(self.user.role, self.user.role),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLORS["sidebar_text"],
            anchor="w",
        ).pack(fill="x")

        # Menu
        menu_frame = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent",
            scrollbar_button_color=COLORS["sidebar_hover"],
            scrollbar_button_hover_color=COLORS["primary"],
        )
        menu_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        ctk.CTkLabel(
            menu_frame,
            text="NAVIGATION",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"),
            text_color=COLORS["sidebar_text"],
            anchor="w",
        ).pack(fill="x", padx=10, pady=(4, 8))

        for key, label in MENUS.get(self.user.role, []):
            icon_name = NAV_ICONS.get(key, "package")
            icon_idle = get_icon(icon_name, 18, COLORS["sidebar_text"])
            icon_active = get_icon(icon_name, 18, "#FFFFFF")
            self._nav_icons[key] = (icon_idle, icon_active)

            btn = ctk.CTkButton(
                menu_frame,
                text=f"  {label}",
                image=icon_idle,
                compound="left",
                anchor="w",
                height=42,
                corner_radius=RADIUS["sm"],
                fg_color="transparent",
                hover_color=COLORS["sidebar_hover"],
                text_color=COLORS["sidebar_text"],
                font=ctk.CTkFont(family=FONT_FAMILY, size=13),
                command=lambda k=key: self.navigate(k),
            )
            btn.pack(fill="x", pady=2, padx=4)
            self._nav_buttons[key] = btn

        # Logout
        logout_icon = get_icon("log-out", 16, "#FFFFFF")
        self._logout_icon = logout_icon
        ctk.CTkButton(
            self.sidebar,
            text="  Déconnexion",
            image=logout_icon,
            compound="left",
            height=42,
            corner_radius=RADIUS["sm"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            command=self.on_logout,
        ).pack(fill="x", padx=12, pady=16)

        # Content area with transition container
        self.content_wrap = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        self.content_wrap.pack(side="right", fill="both", expand=True)
        self.content = ctk.CTkFrame(self.content_wrap, fg_color=COLORS["bg"], corner_radius=0)
        self.content.pack(fill="both", expand=True)

    def navigate(self, key: str) -> None:
        for k, btn in self._nav_buttons.items():
            idle, active = self._nav_icons[k]
            if k == key:
                btn.configure(
                    fg_color=COLORS["sidebar_active"],
                    text_color=COLORS["sidebar_text_active"],
                    image=active,
                    hover_color=COLORS["primary_dark"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["sidebar_text"],
                    image=idle,
                    hover_color=COLORS["sidebar_hover"],
                )

        # Transition : fondu rapide via destroy + place
        for child in self.content.winfo_children():
            child.destroy()

        views = {
            "dashboard": lambda: DashboardView(
                self.content, self.ctx, self.user, navigate=self.navigate
            ),
            "products": lambda: ProductsView(self.content, self.ctx, self.user),
            "categories": lambda: CategoriesView(self.content, self.ctx, self.user),
            "stock": lambda: StockView(self.content, self.ctx, self.user),
            "sales": lambda: SalesView(self.content, self.ctx, self.user),
            "purchases": lambda: PurchasesView(self.content, self.ctx, self.user),
            "customers": lambda: CustomersView(self.content, self.ctx, self.user),
            "suppliers": lambda: SuppliersView(self.content, self.ctx, self.user),
            "orders": lambda: OrdersView(self.content, self.ctx, self.user),
            "users": lambda: UsersView(self.content, self.ctx, self.user),
            "reports": lambda: ReportsView(self.content, self.ctx, self.user),
            "settings": lambda: SettingsView(self.content, self.ctx, self.user),
            "profile": lambda: ProfileView(self.content, self.ctx, self.user),
        }
        factory = views.get(key)
        if not factory:
            return

        view = factory()
        view.pack(fill="both", expand=True)
        self._current_key = key

        # Micro-animation d'entrée : léger décalage puis pack déjà fait
        try:
            view.pack_configure(padx=2)
            self.after(40, lambda: view.winfo_exists() and view.pack_configure(padx=0))
        except Exception:
            pass
