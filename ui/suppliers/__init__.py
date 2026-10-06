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

class SuppliersView(ctk.CTkFrame):
    def __init__(self, master, ctx: AppContext, user: User):
        super().__init__(master, fg_color=COLORS["bg"])
        self.ctx = ctx
        self.user = user
        self._build()
        self.refresh()

    def _build(self) -> None:
        PageHeader(
            self, "Fournisseurs", "Partenaires d'approvisionnement", icon="suppliers"
        ).pack(fill="x", padx=28, pady=(22, 14))
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=28, pady=(0, 10))
        self.search = styled_entry(toolbar, placeholder_text="Rechercher…", width=260)
        self.search.pack(side="left")
        self.search.bind("<KeyRelease>", lambda e: self.refresh())
        SuccessButton(toolbar, text=" Ajouter", width=120, command=self._add).pack(
            side="right", padx=(8, 0)
        )
        SecondaryButton(
            toolbar, text=" Modifier", icon="pencil", width=120, command=self._edit
        ).pack(side="right", padx=(8, 0))
        DangerButton(toolbar, text=" Supprimer", width=120, command=self._delete).pack(
            side="right"
        )

        self.table = DataTable(
            self,
            [
                ("id", "ID", 50),
                ("name", "Nom", 180),
                ("phone", "Téléphone", 110),
                ("email", "Email", 160),
                ("city", "Ville", 90),
                ("gov", "Gouvernorat", 110),
                ("tax", "Matricule fiscal", 140),
            ],
            empty_title="Aucun fournisseur",
            empty_message="Ajoutez un fournisseur pour gérer vos achats.",
        )
        self.table.pack(fill="both", expand=True, padx=28, pady=(0, 24))

    def refresh(self) -> None:
        suppliers = self.ctx.suppliers.search(self.search.get())
        self.table.set_rows(
            [
                (s.id, s.name, s.phone, s.email, s.city, s.governorate, s.tax_id)
                for s in suppliers
            ],
            [s.id for s in suppliers],
        )

    def _selected(self):
        iid = self.table.get_selected()
        return int(iid) if iid else None

    def _form(self, supplier=None) -> None:
        dlg = ctk.CTkToplevel(self)
        style_dialog(dlg, "Fournisseur", "480x600")
        fields = [
            ("name", "Nom", supplier.name if supplier else ""),
            ("phone", "Téléphone", supplier.phone if supplier else ""),
            ("email", "Email", supplier.email if supplier else ""),
            ("address", "Adresse", supplier.address if supplier else ""),
            ("city", "Ville", supplier.city if supplier else ""),
            ("governorate", "Gouvernorat", supplier.governorate if supplier else ""),
            ("tax_id", "Matricule fiscal", supplier.tax_id if supplier else ""),
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
                if supplier:
                    self.ctx.suppliers.update(supplier.id, **data)
                else:
                    self.ctx.suppliers.create(**data)
                dlg.destroy()
                self.refresh()
                toast(self, "Fournisseur enregistré", "success")
            except ValueError as exc:
                show_error("Fournisseurs", str(exc))

        btns = ctk.CTkFrame(dlg, fg_color="transparent")
        btns.pack(fill="x", padx=24, pady=20)
        PrimaryButton(btns, text=" Enregistrer", icon="check", command=save).pack(side="right")
        GhostButton(btns, text="Annuler", command=dlg.destroy).pack(side="right", padx=8)

    def _add(self) -> None:
        self._form()

    def _edit(self) -> None:
        sid = self._selected()
        if not sid:
            show_error("Fournisseurs", "Sélectionnez un fournisseur.")
            return
        self._form(self.ctx.suppliers.get_by_id(sid))

    def _delete(self) -> None:
        sid = self._selected()
        if not sid:
            show_error("Fournisseurs", "Sélectionnez un fournisseur.")
            return
        if ask_confirm("Supprimer", "Supprimer ce fournisseur ?"):
            try:
                self.ctx.suppliers.delete(sid)
                self.refresh()
                toast(self, "Fournisseur supprimé", "success")
            except ValueError as exc:
                show_error("Fournisseurs", str(exc))
