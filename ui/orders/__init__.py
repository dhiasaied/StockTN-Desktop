from __future__ import annotations

import customtkinter as ctk

from models.order import ORDER_STATUSES
from models.user import User
from services.app_context import AppContext
from ui import COLORS, FONT_FAMILY, RADIUS
from ui.common import (
    DataTable,
    GhostButton,
    PageHeader,
    PrimaryButton,
    styled_combo,
    show_error,
    toast,
)
from utils.validators import format_tnd

class OrdersView(ctk.CTkFrame):
    def __init__(self, master, ctx: AppContext, user: User):
        super().__init__(master, fg_color=COLORS["bg"])
        self.ctx = ctx
        self.user = user
        self._build()
        self.refresh()

    def _build(self) -> None:
        title = "Mes commandes" if self.user.role == "client" else "Commandes clients"
        PageHeader(self, title, "Suivi des commandes et statuts", icon="orders").pack(
            fill="x", padx=28, pady=(22, 14)
        )
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=28, pady=(0, 10))

        if self.user.role in ("admin", "seller"):
            ctk.CTkLabel(
                toolbar, text="Nouveau statut :",
                text_color=COLORS["text_muted"],
                font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            ).pack(side="left")
            self.status_box = styled_combo(toolbar, values=ORDER_STATUSES, width=160)
            self.status_box.set(ORDER_STATUSES[0])
            self.status_box.pack(side="left", padx=8)
            PrimaryButton(
                toolbar, text=" Mettre à jour", icon="check", width=140,
                command=self._update_status,
            ).pack(side="left")

        GhostButton(
            toolbar, text=" Actualiser", icon="refresh-cw", width=120, command=self.refresh
        ).pack(side="right")

        self.table = DataTable(
            self,
            [
                ("id", "N°", 60),
                ("date", "Date", 140),
                ("client", "Client", 160),
                ("status", "État", 120),
                ("total", "Total", 110),
                ("updated", "Maj", 140),
            ],
            empty_title="Aucune commande",
            empty_message="Les commandes apparaîtront ici.",
        )
        self.table.pack(fill="both", expand=True, padx=28, pady=(0, 8))

        self.details = ctk.CTkTextbox(
            self,
            height=120,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
        )
        self.details.pack(fill="x", padx=28, pady=(0, 24))
        self.table.tree.bind("<<TreeviewSelect>>", lambda e: self._show_details())

    def refresh(self) -> None:
        if self.user.role == "client":
            orders = (
                self.ctx.orders.get_by_customer(self.user.customer_id)
                if self.user.customer_id
                else []
            )
        else:
            orders = self.ctx.orders.get_all()
        self.table.set_rows(
            [
                (o.id, o.date, o.customer_name, o.status, format_tnd(o.total), o.updated_at)
                for o in orders
            ],
            [o.id for o in orders],
        )

    def _show_details(self) -> None:
        iid = self.table.get_selected()
        self.details.delete("1.0", "end")
        if not iid:
            return
        order = self.ctx.orders.get_by_id(int(iid))
        if not order:
            return
        lines = [f"Commande #{order.id} — {order.status}", "-" * 40]
        for item in order.items:
            lines.append(
                f"{item.product_name}  x{item.quantity}  @ {item.unit_price:.3f} = {item.total:.3f} TND"
            )
        lines.append("-" * 40)
        lines.append(f"Total : {format_tnd(order.total)}")
        if order.note:
            lines.append(f"Note : {order.note}")
        self.details.insert("1.0", "\n".join(lines))

    def _update_status(self) -> None:
        iid = self.table.get_selected()
        if not iid:
            show_error("Commandes", "Sélectionnez une commande.")
            return
        try:
            self.ctx.orders.update_status(int(iid), self.status_box.get())
            toast(self, "Statut mis à jour", "success")
            self.refresh()
            self._show_details()
        except ValueError as exc:
            show_error("Commandes", str(exc))
