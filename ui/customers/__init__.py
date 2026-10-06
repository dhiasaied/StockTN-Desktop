from __future__ import annotations

import customtkinter as ctk

from models.user import User
from services.app_context import AppContext
from ui import COLORS, FONT_FAMILY
from ui.common import (
    DangerButton,
    DataTable,
    GhostButton,
    PageHeader,
    PrimaryButton,
    SecondaryButton,
    SuccessButton,
    ask_confirm,
    show_error,
    style_dialog,
    styled_entry,
    toast,
)

class CustomersView(ctk.CTkFrame):
    def __init__(self, master, ctx: AppContext, user: User):
        super().__init__(master, fg_color=COLORS["bg"])
        self.ctx = ctx
        self.user = user
        self.can_edit = user.role in ("admin", "seller")
        self._build()
        self.refresh()

    def _build(self) -> None:
        PageHeader(self, "Clients", "Fichier clients", icon="customers").pack(
            fill="x", padx=28, pady=(22, 14)
        )
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=28, pady=(0, 10))
        self.search = styled_entry(toolbar, placeholder_text="Rechercher…", width=260)
        self.search.pack(side="left")
        self.search.bind("<KeyRelease>", lambda e: self.refresh())

        if self.can_edit:
            SuccessButton(toolbar, text=" Ajouter", width=120, command=self._add).pack(
                side="right", padx=(8, 0)
            )
            SecondaryButton(
                toolbar, text=" Modifier", icon="pencil", width=120, command=self._edit
            ).pack(side="right", padx=(8, 0))
            if self.user.role == "admin":
                DangerButton(toolbar, text=" Supprimer", width=120, command=self._delete).pack(
                    side="right"
                )

        self.table = DataTable(
            self,
            [
                ("id", "ID", 50),
                ("name", "Nom", 160),
                ("phone", "Téléphone", 120),
                ("email", "Email", 180),
                ("city", "Ville", 100),
                ("created", "Créé le", 140),
            ],
            empty_title="Aucun client",
            empty_message="Ajoutez un client pour commencer.",
        )
        self.table.pack(fill="both", expand=True, padx=28, pady=(0, 24))

    def refresh(self) -> None:
        customers = self.ctx.customers.search(self.search.get())
        self.table.set_rows(
            [
                (c.id, c.full_name, c.phone, c.email, c.city, c.created_at)
                for c in customers
            ],
            [c.id for c in customers],
        )

    def _selected(self):
        iid = self.table.get_selected()
        return int(iid) if iid else None

    def _form(self, customer=None) -> None:
        dlg = ctk.CTkToplevel(self)
        style_dialog(dlg, "Client", "460x520")
        fields = [
            ("last_name", "Nom", customer.last_name if customer else ""),
            ("first_name", "Prénom", customer.first_name if customer else ""),
            ("phone", "Téléphone", customer.phone if customer else ""),
            ("email", "Email", customer.email if customer else ""),
            ("address", "Adresse", customer.address if customer else ""),
            ("city", "Ville", customer.city if customer else ""),
        ]
        entries = {}
        for key, label, value in fields:
            ctk.CTkLabel(
                dlg, text=label, anchor="w", text_color=COLORS["text_muted"],
                font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            ).pack(fill="x", padx=24, pady=(10, 0))
            e = styled_entry(dlg)
            e.insert(0, value)
            e.pack(fill="x", padx=24, pady=(4, 0))
            entries[key] = e

        def save():
            try:
                data = {k: e.get() for k, e in entries.items()}
                if customer:
                    self.ctx.customers.update(customer.id, **data)
                else:
                    self.ctx.customers.create(**data)
                dlg.destroy()
                self.refresh()
                toast(self, "Client enregistré", "success")
            except ValueError as exc:
                show_error("Clients", str(exc))

        btns = ctk.CTkFrame(dlg, fg_color="transparent")
        btns.pack(fill="x", padx=24, pady=20)
        PrimaryButton(btns, text=" Enregistrer", icon="check", command=save).pack(side="right")
        GhostButton(btns, text="Annuler", command=dlg.destroy).pack(side="right", padx=8)

    def _add(self) -> None:
        self._form()

    def _edit(self) -> None:
        cid = self._selected()
        if not cid:
            show_error("Clients", "Sélectionnez un client.")
            return
        self._form(self.ctx.customers.get_by_id(cid))

    def _delete(self) -> None:
        cid = self._selected()
        if not cid:
            show_error("Clients", "Sélectionnez un client.")
            return
        if ask_confirm("Supprimer", "Supprimer ce client ?"):
            try:
                self.ctx.customers.delete(cid)
                self.refresh()
                toast(self, "Client supprimé", "success")
            except ValueError as exc:
                show_error("Clients", str(exc))
