from __future__ import annotations

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from models.user import User
from services.app_context import AppContext
from ui import COLORS, FONT_FAMILY, RADIUS
from ui.common import (
    ContentCard,
    DataTable,
    EmptyState,
    PageHeader,
    PrimaryButton,
    StatCard,
)
from ui.icons import get_icon
from utils.validators import format_tnd

class DashboardView(ctk.CTkScrollableFrame):
    def __init__(self, master, ctx: AppContext, user: User, navigate=None):
        super().__init__(master, fg_color=COLORS["bg"], scrollbar_button_color=COLORS["border"])
        self.ctx = ctx
        self.user = user
        self.navigate = navigate
        self._build()

    def _build(self) -> None:
        PageHeader(
            self,
            "Tableau de bord",
            f"Bienvenue, {self.user.full_name}",
            icon="dashboard",
        ).pack(fill="x", padx=28, pady=(22, 18))

        if self.user.role == "admin":
            self._build_admin()
        elif self.user.role == "seller":
            self._build_seller()
        else:
            self._build_client()

    def _cards_row(self, cards: list[tuple]) -> None:
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=28, pady=(0, 14))
        for i in range(len(cards)):
            row.grid_columnconfigure(i, weight=1, uniform="cards")
        for i, item in enumerate(cards):
            title, value, sub, accent, icon = item
            StatCard(row, title, value, sub, accent, icon=icon).grid(
                row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 10, 0)
            )

    def _build_admin(self) -> None:
        products = self.ctx.products.get_all()
        low = self.ctx.products.get_low_stock()
        out = self.ctx.products.get_out_of_stock()
        sales_today = self.ctx.sales.get_today()
        purchases_today = self.ctx.purchases.get_today()

        self._cards_row(
            [
                ("Produits", str(len(products)), "Catalogue actif", COLORS["primary"], "products"),
                ("Catégories", str(len(self.ctx.categories.get_all())), "Organisation", COLORS["primary_light"], "categories"),
                ("Clients", str(len(self.ctx.customers.get_all())), "Fichier clients", COLORS["success"], "customers"),
                ("Fournisseurs", str(len(self.ctx.suppliers.get_all())), "Partenaires", COLORS["info"], "suppliers"),
            ]
        )
        self._cards_row(
            [
                ("Stock faible", str(len(low)), "À réapprovisionner", COLORS["warning"], "alert-triangle"),
                ("Ruptures", str(len(out)), "Stock = 0", COLORS["danger"], "x-circle"),
                (
                    "Ventes du jour",
                    format_tnd(sum(s.total for s in sales_today)),
                    f"{len(sales_today)} ticket(s)",
                    COLORS["success"],
                    "sales",
                ),
                (
                    "Achats du jour",
                    format_tnd(sum(p.total for p in purchases_today)),
                    f"{len(purchases_today)} bon(s)",
                    COLORS["primary"],
                    "purchases",
                ),
            ]
        )

        chart_card = ContentCard(self, title="Ventes des 7 derniers jours", icon="reports")
        chart_card.pack(fill="both", expand=True, padx=28, pady=(4, 14))
        self._draw_sales_chart(chart_card)

        alert_card = ContentCard(self, title="Alertes stock", icon="bell")
        alert_card.pack(fill="both", expand=True, padx=28, pady=(0, 28))
        table = DataTable(
            alert_card,
            [
                ("code", "Code", 100),
                ("name", "Produit", 220),
                ("qty", "Stock", 80),
                ("min", "Min", 80),
                ("status", "État", 120),
            ],
            empty_title="Aucune alerte",
            empty_message="Tous les stocks sont à un niveau satisfaisant.",
        )
        table.pack(fill="both", expand=True, padx=12, pady=(4, 12))
        rows, iids = [], []
        for p in out + low:
            status = "Rupture" if p.is_out_of_stock else "Stock faible"
            rows.append((p.code, p.name, p.quantity, p.min_stock, status))
            iids.append(p.id)
        table.set_rows(rows, iids)

    def _draw_sales_chart(self, parent) -> None:
        from datetime import datetime, timedelta

        days, totals = [], []
        for i in range(6, -1, -1):
            day = datetime.now() - timedelta(days=i)
            key = day.strftime("%Y-%m-%d")
            days.append(day.strftime("%d/%m"))
            totals.append(
                sum(s.total for s in self.ctx.sales.get_all() if s.date.startswith(key))
            )

        if sum(totals) == 0:
            EmptyState(
                parent,
                title="Pas encore de ventes",
                message="Les ventes des 7 derniers jours apparaîtront ici.",
                icon="bar-chart-3",
            ).pack(fill="x", pady=20)
            return

        fig = Figure(figsize=(8, 2.6), dpi=100)
        fig.patch.set_facecolor("white")
        ax = fig.add_subplot(111)
        bars = ax.bar(days, totals, color=COLORS["primary"], width=0.55, zorder=3)
        for bar in bars:
            bar.set_alpha(0.92)
        ax.set_ylabel("TND", color=COLORS["text_muted"], fontsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(COLORS["border"])
        ax.spines["bottom"].set_color(COLORS["border"])
        ax.tick_params(colors=COLORS["text_muted"], labelsize=9)
        ax.set_facecolor("white")
        ax.yaxis.grid(True, color=COLORS["border"], linestyle="--", linewidth=0.6, zorder=0)
        ax.set_axisbelow(True)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=(0, 14))

    def _build_seller(self) -> None:
        available = [p for p in self.ctx.products.get_all() if p.quantity > 0]
        low = self.ctx.products.get_low_stock()
        sales_today = self.ctx.sales.get_today()

        self._cards_row(
            [
                ("Produits dispo.", str(len(available)), "En stock", COLORS["primary"], "products"),
                ("Stock faible", str(len(low)), "Alertes", COLORS["warning"], "alert-triangle"),
                (
                    "Ventes du jour",
                    format_tnd(sum(s.total for s in sales_today)),
                    f"{len(sales_today)} vente(s)",
                    COLORS["success"],
                    "sales",
                ),
            ]
        )

        actions = ContentCard(self, title="Accès rapide", icon="zap")
        actions.pack(fill="x", padx=28, pady=(4, 14))
        PrimaryButton(
            actions,
            text="  Ouvrir la caisse",
            icon="shopping-cart",
            height=44,
            width=200,
            command=lambda: self.navigate and self.navigate("sales"),
        ).pack(padx=16, pady=(4, 16), anchor="w")

        table_frame = ContentCard(self, title="Dernières ventes", icon="sales")
        table_frame.pack(fill="both", expand=True, padx=28, pady=(0, 28))
        table = DataTable(
            table_frame,
            [
                ("id", "N°", 60),
                ("date", "Date", 140),
                ("client", "Client", 160),
                ("total", "Total", 120),
            ],
            empty_title="Aucune vente",
            empty_message="Les ventes récentes s'afficheront ici.",
        )
        table.pack(fill="both", expand=True, padx=12, pady=(4, 12))
        rows = [
            (s.id, s.date, s.customer_name, format_tnd(s.total))
            for s in self.ctx.sales.get_all()[:15]
        ]
        table.set_rows(rows)

    def _build_client(self) -> None:
        customer_id = self.user.customer_id
        available = [p for p in self.ctx.products.get_all() if p.quantity > 0]
        orders = (
            self.ctx.orders.get_by_customer(customer_id) if customer_id else []
        )
        sales = (
            self.ctx.sales.get_by_customer(customer_id) if customer_id else []
        )

        self._cards_row(
            [
                ("Produits disponibles", str(len(available)), "Catalogue", COLORS["primary"], "products"),
                ("Commandes", str(len(orders)), "Total", COLORS["primary_light"], "orders"),
                ("Achats", str(len(sales)), "Historique", COLORS["success"], "sales"),
            ]
        )

        profile = self.ctx.customers.get_by_id(customer_id) if customer_id else None
        info = ContentCard(self, title="Mon profil", icon="profile")
        info.pack(fill="x", padx=28, pady=(4, 14))
        if profile:
            row = ctk.CTkFrame(info, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=(4, 16))
            for label, value, icon in (
                ("Nom", profile.full_name, "user"),
                ("Téléphone", profile.phone, "phone"),
                ("Email", profile.email, "mail"),
                ("Adresse", f"{profile.address}, {profile.city}", "map-pin"),
            ):
                item = ctk.CTkFrame(row, fg_color=COLORS["surface_hover"], corner_radius=RADIUS["sm"])
                item.pack(fill="x", pady=3)
                img = get_icon(icon, 14, COLORS["primary"])
                inner = ctk.CTkFrame(item, fg_color="transparent")
                inner.pack(fill="x", padx=12, pady=8)
                ctk.CTkLabel(inner, text="", image=img).pack(side="left", padx=(0, 8))
                if not hasattr(self, "_p_icons"):
                    self._p_icons = []
                self._p_icons.append(img)
                ctk.CTkLabel(
                    inner,
                    text=f"{label}  ·  {value}",
                    text_color=COLORS["text_secondary"],
                    font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                    anchor="w",
                ).pack(side="left")
        else:
            EmptyState(
                info,
                title="Profil non lié",
                message="Aucun profil client associé à ce compte.",
                icon="user",
            ).pack(fill="x")

        orders_frame = ContentCard(self, title="Commandes récentes", icon="orders")
        orders_frame.pack(fill="both", expand=True, padx=28, pady=(0, 28))
        table = DataTable(
            orders_frame,
            [
                ("id", "N°", 60),
                ("date", "Date", 140),
                ("status", "État", 120),
                ("total", "Total", 120),
            ],
            empty_title="Aucune commande",
            empty_message="Vos commandes apparaîtront ici.",
        )
        table.pack(fill="both", expand=True, padx=12, pady=(4, 12))
        table.set_rows(
            [(o.id, o.date, o.status, format_tnd(o.total)) for o in orders[:20]]
        )
