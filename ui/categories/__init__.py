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

class CategoriesView(ctk.CTkFrame):
    def __init__(self, master, ctx: AppContext, user: User):
        super().__init__(master, fg_color=COLORS["bg"])
        self.ctx = ctx
        self.user = user
        self._build()
        self.refresh()

    def _build(self) -> None:
        PageHeader(self, "Catégories", "Organisation du catalogue", icon="categories").pack(
            fill="x", padx=28, pady=(22, 14)
        )
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=28, pady=(0, 10))
        self.search = styled_entry(toolbar, placeholder_text="Rechercher…", width=240)
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
            [("id", "ID", 60), ("name", "Nom", 200), ("desc", "Description", 360)],
            empty_title="Aucune catégorie",
            empty_message="Créez une catégorie pour organiser vos produits.",
        )
        self.table.pack(fill="both", expand=True, padx=28, pady=(0, 24))

    def refresh(self) -> None:
        cats = self.ctx.categories.search(self.search.get())
        self.table.set_rows(
            [(c.id, c.name, c.description) for c in cats],
            [c.id for c in cats],
        )

    def _selected(self):
        iid = self.table.get_selected()
        return int(iid) if iid else None

    def _form(self, category=None) -> None:
        dlg = ctk.CTkToplevel(self)
        style_dialog(dlg, "Catégorie", "420x300")
        ctk.CTkLabel(
            dlg, text="Nom", anchor="w", text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        ).pack(fill="x", padx=24, pady=(20, 0))
        name = styled_entry(dlg)
        name.pack(fill="x", padx=24, pady=(4, 0))
        ctk.CTkLabel(
            dlg, text="Description", anchor="w", text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        ).pack(fill="x", padx=24, pady=(12, 0))
        desc = styled_entry(dlg)
        desc.pack(fill="x", padx=24, pady=(4, 0))
        if category:
            name.insert(0, category.name)
            desc.insert(0, category.description)

        def save():
            try:
                if category:
                    self.ctx.categories.update(category.id, name.get(), desc.get())
                else:
                    self.ctx.categories.create(name.get(), desc.get())
                dlg.destroy()
                self.refresh()
                toast(self, "Catégorie enregistrée", "success")
            except ValueError as exc:
                show_error("Catégories", str(exc))

        btns = ctk.CTkFrame(dlg, fg_color="transparent")
        btns.pack(fill="x", padx=24, pady=24)
        PrimaryButton(btns, text=" Enregistrer", icon="check", command=save).pack(side="right")
        GhostButton(btns, text="Annuler", command=dlg.destroy).pack(side="right", padx=8)

    def _add(self) -> None:
        self._form()

    def _edit(self) -> None:
        cid = self._selected()
        if not cid:
            show_error("Catégories", "Sélectionnez une catégorie.")
            return
        self._form(self.ctx.categories.get_by_id(cid))

    def _delete(self) -> None:
        cid = self._selected()
        if not cid:
            show_error("Catégories", "Sélectionnez une catégorie.")
            return
        if ask_confirm("Supprimer", "Supprimer cette catégorie ?"):
            try:
                self.ctx.categories.delete(cid)
                self.refresh()
                toast(self, "Catégorie supprimée", "success")
            except ValueError as exc:
                show_error("Catégories", str(exc))
