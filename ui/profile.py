from __future__ import annotations

import customtkinter as ctk

from models.user import User
from services.app_context import AppContext
from ui import COLORS, FONT_FAMILY, RADIUS, ROLE_LABELS, SPACING
from ui.common import ContentCard, DataTable, EmptyState, PageHeader, StatCard, StatusBanner
from ui.icons import get_icon
from utils.validators import format_tnd


class ProfileView(ctk.CTkScrollableFrame):
    def __init__(self, master, ctx: AppContext, user: User):
        super().__init__(
            master,
            fg_color=COLORS["bg"],
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["primary"],
        )
        self.ctx = ctx
        self.user = user
        self._icon_refs: list = []
        self._build()

    def _build(self) -> None:
        px = SPACING["page_x"]
        PageHeader(
            self,
            "Mon profil",
            "Informations personnelles et historique d'achats",
            icon="profile",
        ).pack(fill="x", padx=px, pady=(SPACING["page_y"], 18))

        customer = (
            self.ctx.customers.get_by_id(self.user.customer_id)
            if self.user.customer_id
            else None
        )
        sales = (
            self.ctx.sales.get_by_customer(self.user.customer_id)
            if self.user.customer_id
            else []
        )
        orders = (
            self.ctx.orders.get_by_customer(self.user.customer_id)
            if self.user.customer_id
            else []
        )

        display_name = customer.full_name if customer else self.user.full_name
        self._build_hero(display_name, customer)
        self._build_stats(sales, orders)
        self._build_details(customer)
        self._build_history(sales)

    # ─── Hero profil ────────────────────────────────────────────────────────

    def _build_hero(self, display_name: str, customer) -> None:
        card = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        card.pack(fill="x", padx=SPACING["page_x"], pady=(0, 14))

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=22, pady=22)

        # Ligne principale : avatar + identité
        top = ctk.CTkFrame(body, fg_color="transparent")
        top.pack(fill="x")

        initials = "".join(p[0] for p in display_name.split()[:2]).upper() or "?"
        avatar_wrap = ctk.CTkFrame(top, fg_color="transparent", width=88, height=88)
        avatar_wrap.pack(side="left", padx=(0, 20))
        avatar_wrap.pack_propagate(False)

        # Anneau discret autour de l'avatar
        ring = ctk.CTkFrame(
            avatar_wrap,
            fg_color=COLORS["primary_soft"],
            width=88,
            height=88,
            corner_radius=44,
        )
        ring.place(relx=0.5, rely=0.5, anchor="center")
        ring.pack_propagate(False)

        avatar = ctk.CTkFrame(
            ring,
            fg_color=COLORS["primary"],
            width=72,
            height=72,
            corner_radius=36,
        )
        avatar.place(relx=0.5, rely=0.5, anchor="center")
        avatar.pack_propagate(False)
        ctk.CTkLabel(
            avatar,
            text=initials,
            font=ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold"),
            text_color="#FFFFFF",
        ).place(relx=0.5, rely=0.5, anchor="center")

        identity = ctk.CTkFrame(top, fg_color="transparent")
        identity.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            identity,
            text=display_name,
            font=ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold"),
            text_color=COLORS["text"],
            anchor="w",
        ).pack(fill="x", pady=(6, 0))

        meta = ctk.CTkFrame(identity, fg_color="transparent")
        meta.pack(fill="x", pady=(8, 0))

        role_label = ROLE_LABELS.get(self.user.role, self.user.role)
        self._badge(meta, role_label, COLORS["primary"], COLORS["primary_soft"]).pack(
            side="left", padx=(0, 8)
        )

        status_text = "Compte actif" if self.user.active else "Compte inactif"
        status_fg = COLORS["success"] if self.user.active else COLORS["danger"]
        status_bg = COLORS["success_soft"] if self.user.active else COLORS["danger_soft"]
        self._badge(meta, status_text, status_fg, status_bg).pack(side="left")

        # Identifiant compte
        account_row = ctk.CTkFrame(identity, fg_color="transparent")
        account_row.pack(fill="x", pady=(10, 0))
        user_icon = get_icon("user", 14, COLORS["text_muted"])
        self._icon_refs.append(user_icon)
        ctk.CTkLabel(account_row, text="", image=user_icon).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(
            account_row,
            text=f"@{self.user.username}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            text_color=COLORS["text_muted"],
            anchor="w",
        ).pack(side="left")

        if not customer and self.user.role == "client":
            StatusBanner(
                body,
                "Aucun fiche client liée à ce compte.",
                kind="warning",
            ).pack(fill="x", pady=(16, 0))

    def _badge(self, master, text: str, fg: str, bg: str) -> ctk.CTkFrame:
        badge = ctk.CTkFrame(
            master,
            fg_color=bg,
            corner_radius=RADIUS["sm"],
            border_width=1,
            border_color=fg,
        )
        ctk.CTkLabel(
            badge,
            text=text,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=fg,
            padx=10,
            pady=4,
        ).pack()
        return badge

    # ─── Statistiques ───────────────────────────────────────────────────────

    def _build_stats(self, sales, orders) -> None:
        total_spent = sum(s.total for s in sales)
        sorted_sales = sorted(sales, key=lambda s: s.date or "", reverse=True)
        last_purchase = sorted_sales[0].date if sorted_sales else "—"

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=SPACING["page_x"], pady=(0, 14))
        cards = [
            ("Achats", str(len(sales)), "Historique", COLORS["primary"], "sales"),
            ("Commandes", str(len(orders)), "Total", COLORS["info"], "orders"),
            ("Dépenses", format_tnd(total_spent), "Cumul", COLORS["success"], "trending-up"),
            ("Dernier achat", last_purchase[:10] if last_purchase != "—" else "—", "Date", COLORS["warning"], "calendar"),
        ]
        for i in range(len(cards)):
            row.grid_columnconfigure(i, weight=1, uniform="profile_stats")
        for i, (title, value, sub, accent, icon) in enumerate(cards):
            StatCard(row, title, value, sub, accent, icon=icon).grid(
                row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 10, 0)
            )

    # ─── Coordonnées & infos personnelles ───────────────────────────────────

    def _build_details(self, customer) -> None:
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=SPACING["page_x"], pady=(0, 14))
        grid.grid_columnconfigure(0, weight=1, uniform="profile_cols")
        grid.grid_columnconfigure(1, weight=1, uniform="profile_cols")

        # Coordonnées
        contact_card = ContentCard(grid, title="Coordonnées", icon="mail")
        contact_card.grid(row=0, column=0, sticky="nsew", padx=(0, 7))

        if customer:
            contact_items = [
                ("Téléphone", customer.phone or "—", "phone"),
                ("Email", customer.email or self.user.email or "—", "mail"),
                ("Adresse", customer.address or "—", "map-pin"),
                ("Ville", customer.city or "—", "map-pin"),
            ]
        else:
            contact_items = [
                ("Téléphone", self.user.phone or "—", "phone"),
                ("Email", self.user.email or "—", "mail"),
                ("Adresse", "—", "map-pin"),
                ("Ville", "—", "map-pin"),
            ]

        contact_body = ctk.CTkFrame(contact_card, fg_color="transparent")
        contact_body.pack(fill="both", expand=True, padx=16, pady=(8, 16))
        for label, value, icon in contact_items:
            self._info_row(contact_body, label, value, icon)

        # Informations personnelles / compte
        info_card = ContentCard(grid, title="Informations personnelles", icon="profile")
        info_card.grid(row=0, column=1, sticky="nsew", padx=(7, 0))

        info_items = [
            ("Nom complet", customer.full_name if customer else self.user.full_name, "user"),
            ("Nom d'utilisateur", self.user.username, "user"),
            ("Rôle", ROLE_LABELS.get(self.user.role, self.user.role), "layers"),
            (
                "Client depuis",
                (customer.created_at[:10] if customer and customer.created_at else "—"),
                "calendar",
            ),
        ]
        if customer:
            info_items.append(("N° client", str(customer.id), "clipboard-list"))
        else:
            info_items.append(("Fiche client", "Non liée", "alert-triangle"))

        info_body = ctk.CTkFrame(info_card, fg_color="transparent")
        info_body.pack(fill="both", expand=True, padx=16, pady=(8, 16))
        for label, value, icon in info_items:
            self._info_row(info_body, label, value, icon)

    def _info_row(self, master, label: str, value: str, icon: str) -> None:
        row = ctk.CTkFrame(
            master,
            fg_color=COLORS["surface_hover"],
            corner_radius=RADIUS["sm"],
            border_width=1,
            border_color=COLORS["border"],
        )
        row.pack(fill="x", pady=4)

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)

        icon_badge = ctk.CTkFrame(
            inner,
            fg_color=COLORS["primary_soft"],
            width=34,
            height=34,
            corner_radius=RADIUS["sm"],
        )
        icon_badge.pack(side="left", padx=(0, 12))
        icon_badge.pack_propagate(False)
        img = get_icon(icon, 15, COLORS["primary"])
        self._icon_refs.append(img)
        ctk.CTkLabel(icon_badge, text="", image=img).place(relx=0.5, rely=0.5, anchor="center")

        text_col = ctk.CTkFrame(inner, fg_color="transparent")
        text_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            text_col,
            text=label,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLORS["text_muted"],
            anchor="w",
        ).pack(fill="x")
        ctk.CTkLabel(
            text_col,
            text=value or "—",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLORS["text"],
            anchor="w",
        ).pack(fill="x", pady=(1, 0))

        # Hover subtil sur la bordure
        def on_enter(_e=None, r=row):
            try:
                r.configure(border_color=COLORS["primary"])
            except Exception:
                pass

        def on_leave(_e=None, r=row):
            try:
                r.configure(border_color=COLORS["border"])
            except Exception:
                pass

        for w in (row, inner, text_col, icon_badge):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

    # ─── Historique d'achats ─────────────────────────────────────────────────

    def _build_history(self, sales) -> None:
        history = ContentCard(self, title="Historique d'achats", icon="sales")
        history.pack(fill="both", expand=True, padx=SPACING["page_x"], pady=(0, 28))

        # Sous-titre contextuel
        count = len(sales)
        subtitle = (
            f"{count} transaction{'s' if count != 1 else ''} enregistrée{'s' if count != 1 else ''}"
            if count
            else "Aucune transaction pour le moment"
        )
        ctk.CTkLabel(
            history,
            text=subtitle,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLORS["text_muted"],
            anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 4))

        if not sales:
            EmptyState(
                history,
                title="Aucun achat",
                message="Votre historique d'achats apparaîtra ici après vos premières commandes.",
                icon="shopping-bag",
            ).pack(fill="both", expand=True, pady=(0, 8))
            return

        table = DataTable(
            history,
            [
                ("id", "N°", 70),
                ("date", "Date", 160),
                ("total", "Total", 130),
                ("pay", "Paiement", 120),
            ],
            empty_title="Aucun achat",
            empty_message="Votre historique d'achats apparaîtra ici.",
        )
        table.pack(fill="both", expand=True, padx=12, pady=(4, 14))
        table.set_rows(
            [(s.id, s.date, format_tnd(s.total), s.payment_method) for s in sales],
            [s.id for s in sales],
        )
