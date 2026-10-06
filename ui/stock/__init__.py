from __future__ import annotations

import customtkinter as ctk

from models.user import User
from services.app_context import AppContext
from ui import COLORS, FONT_FAMILY, RADIUS
from ui.common import (
    DataTable,
    PageHeader,
    PrimaryButton,
    show_error,
    styled_combo,
    styled_entry,
    toast,
)

class StockView(ctk.CTkFrame):
    def __init__(self, master, ctx: AppContext, user: User):
        super().__init__(master, fg_color=COLORS["bg"])
        self.ctx = ctx
        self.user = user
        self._build()
        self.refresh()

    def _build(self) -> None:
        PageHeader(self, "Stock", "Entrées, sorties et alertes", icon="stock").pack(
            fill="x", padx=28, pady=(22, 14)
        )
        tabs = ctk.CTkTabview(
            self,
            fg_color=COLORS["bg"],
            corner_radius=RADIUS["md"],
            segmented_button_fg_color=COLORS["surface"],
            segmented_button_selected_color=COLORS["primary"],
            segmented_button_selected_hover_color=COLORS["primary_dark"],
            segmented_button_unselected_color=COLORS["surface"],
            segmented_button_unselected_hover_color=COLORS["surface_hover"],
            text_color=COLORS["text"],
            border_width=1,
            border_color=COLORS["border"],
        )
        tabs.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        move = tabs.add("Mouvement")
        hist = tabs.add("Historique")
        alerts = tabs.add("Alertes")

        form = ctk.CTkFrame(
            move,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        form.pack(fill="x", padx=8, pady=12)
        products = [f"{p.id} - {p.name} (stock: {p.quantity})" for p in self.ctx.products.get_all()]
        ctk.CTkLabel(
            form, text="Produit", text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        ).grid(row=0, column=0, padx=16, pady=12, sticky="w")
        self.product_box = styled_combo(form, values=products or ["—"], width=320)
        if products:
            self.product_box.set(products[0])
        self.product_box.grid(row=0, column=1, padx=8, pady=12)

        ctk.CTkLabel(
            form, text="Type", text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        ).grid(row=1, column=0, padx=16, pady=12, sticky="w")
        self.type_box = styled_combo(form, values=["Entrée", "Sortie"], width=160)
        self.type_box.set("Entrée")
        self.type_box.grid(row=1, column=1, sticky="w", padx=8, pady=12)

        ctk.CTkLabel(
            form, text="Quantité", text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        ).grid(row=2, column=0, padx=16, pady=12, sticky="w")
        self.qty = styled_entry(form, width=120)
        self.qty.insert(0, "1")
        self.qty.grid(row=2, column=1, sticky="w", padx=8, pady=12)

        ctk.CTkLabel(
            form, text="Motif", text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        ).grid(row=3, column=0, padx=16, pady=12, sticky="w")
        self.reason = styled_entry(form, width=320)
        self.reason.grid(row=3, column=1, padx=8, pady=12)

        PrimaryButton(
            form, text=" Enregistrer le mouvement", icon="check",
            command=self._save_movement,
        ).grid(row=4, column=1, sticky="w", padx=8, pady=16)

        self.history = DataTable(
            hist,
            [
                ("id", "ID", 50),
                ("date", "Date", 140),
                ("type", "Type", 80),
                ("product", "Produit", 200),
                ("qty", "Qté", 60),
                ("reason", "Motif", 160),
                ("user", "Utilisateur", 100),
            ],
            empty_title="Aucun mouvement",
            empty_message="Les entrées et sorties apparaîtront ici.",
        )
        self.history.pack(fill="both", expand=True, padx=8, pady=8)

        self.alerts = DataTable(
            alerts,
            [
                ("code", "Code", 90),
                ("name", "Produit", 220),
                ("qty", "Stock", 70),
                ("min", "Min", 70),
                ("status", "Alerte", 120),
            ],
            empty_title="Aucune alerte",
            empty_message="Tous les stocks sont dans les seuils.",
        )
        self.alerts.pack(fill="both", expand=True, padx=8, pady=8)

    def _save_movement(self) -> None:
        sel = self.product_box.get()
        if " - " not in sel:
            return
        pid = int(sel.split(" - ", 1)[0])
        try:
            qty = int(self.qty.get())
            reason = self.reason.get().strip()
            if self.type_box.get() == "Entrée":
                self.ctx.stock.add_entry(
                    pid, qty, reason, self.user.id, self.user.username
                )
            else:
                self.ctx.stock.add_exit(
                    pid, qty, reason, self.user.id, self.user.username
                )
            toast(self, "Mouvement enregistré", "success")
            self.reason.delete(0, "end")
            self.refresh()
            products = [
                f"{p.id} - {p.name} (stock: {p.quantity})"
                for p in self.ctx.products.get_all()
            ]
            self.product_box.configure(values=products or ["—"])
        except ValueError as exc:
            show_error("Stock", str(exc))

    def refresh(self) -> None:
        movements = self.ctx.stock.get_all()
        self.history.set_rows(
            [
                (
                    m.id, m.date,
                    "Entrée" if m.movement_type == "entry" else "Sortie",
                    m.product_name, m.quantity, m.reason, m.username,
                )
                for m in movements
            ],
            [m.id for m in movements],
        )
        alerts = self.ctx.products.get_out_of_stock() + self.ctx.products.get_low_stock()
        self.alerts.set_rows(
            [
                (
                    p.code, p.name, p.quantity, p.min_stock,
                    "Rupture" if p.is_out_of_stock else "Stock faible",
                )
                for p in alerts
            ],
            [p.id for p in alerts],
        )
