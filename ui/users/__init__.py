from __future__ import annotations

import customtkinter as ctk

from models.user import User
from services.app_context import AppContext
from ui import COLORS, FONT_FAMILY, ROLE_LABELS
from ui.common import (
    DangerButton,
    DataTable,
    GhostButton,
    PageHeader,
    PrimaryButton,
    SecondaryButton,
    SuccessButton,
    WarningButton,
    ask_confirm,
    show_error,
    style_dialog,
    styled_combo,
    styled_entry,
    toast,
)

class UsersView(ctk.CTkFrame):
    def __init__(self, master, ctx: AppContext, user: User):
        super().__init__(master, fg_color=COLORS["bg"])
        self.ctx = ctx
        self.user = user
        self._build()
        self.refresh()

    def _build(self) -> None:
        PageHeader(self, "Utilisateurs", "Comptes et rôles", icon="users").pack(
            fill="x", padx=28, pady=(22, 14)
        )
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=28, pady=(0, 10))
        SuccessButton(toolbar, text=" Ajouter", width=120, command=self._add).pack(
            side="right", padx=(8, 0)
        )
        SecondaryButton(
            toolbar, text=" Modifier", icon="pencil", width=120, command=self._edit
        ).pack(side="right", padx=(8, 0))
        WarningButton(
            toolbar, text=" Activer/Désactiver", icon="alert-triangle", width=160,
            command=self._toggle,
        ).pack(side="right", padx=(8, 0))
        DangerButton(toolbar, text=" Supprimer", width=120, command=self._delete).pack(
            side="right"
        )

        self.table = DataTable(
            self,
            [
                ("id", "ID", 50),
                ("username", "Identifiant", 120),
                ("name", "Nom", 160),
                ("role", "Rôle", 120),
                ("email", "Email", 180),
                ("active", "Statut", 90),
            ],
            empty_title="Aucun utilisateur",
            empty_message="Ajoutez un compte pour commencer.",
        )
        self.table.pack(fill="both", expand=True, padx=28, pady=(0, 24))

    def refresh(self) -> None:
        users = self.ctx.auth.get_all()
        self.table.set_rows(
            [
                (
                    u.id, u.username, u.full_name,
                    ROLE_LABELS.get(u.role, u.role),
                    u.email,
                    "Actif" if u.active else "Inactif",
                )
                for u in users
            ],
            [u.id for u in users],
        )

    def _selected(self):
        iid = self.table.get_selected()
        return int(iid) if iid else None

    def _form(self, user=None) -> None:
        dlg = ctk.CTkToplevel(self)
        style_dialog(dlg, "Utilisateur", "460x560")
        fields = [
            ("username", "Identifiant", user.username if user else ""),
            ("first_name", "Prénom", user.first_name if user else ""),
            ("last_name", "Nom", user.last_name if user else ""),
            ("email", "Email", user.email if user else ""),
            ("phone", "Téléphone", user.phone if user else ""),
            ("password", "Mot de passe" + (" (laisser vide = inchangé)" if user else ""), ""),
        ]
        entries = {}
        for key, label, value in fields:
            ctk.CTkLabel(
                dlg, text=label, anchor="w", text_color=COLORS["text_muted"],
                font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            ).pack(fill="x", padx=24, pady=(10, 0))
            show = "•" if key == "password" else ""
            e = styled_entry(dlg, show=show)
            e.insert(0, value)
            e.pack(fill="x", padx=24, pady=(4, 0))
            entries[key] = e

        ctk.CTkLabel(
            dlg, text="Rôle", anchor="w", text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        ).pack(fill="x", padx=24, pady=(10, 0))
        role_box = styled_combo(dlg, values=["admin", "seller", "client"])
        role_box.set(user.role if user else "seller")
        role_box.pack(fill="x", padx=24, pady=(4, 0))

        def save():
            try:
                data = {
                    "username": entries["username"].get(),
                    "first_name": entries["first_name"].get(),
                    "last_name": entries["last_name"].get(),
                    "email": entries["email"].get(),
                    "phone": entries["phone"].get(),
                    "role": role_box.get(),
                }
                pwd = entries["password"].get()
                if user:
                    if pwd:
                        data["password"] = pwd
                    self.ctx.auth.update_user(user.id, **data)
                else:
                    if not pwd:
                        raise ValueError("Le mot de passe est obligatoire.")
                    self.ctx.auth.create_user(password=pwd, **data)
                dlg.destroy()
                self.refresh()
                toast(self, "Utilisateur enregistré", "success")
            except ValueError as exc:
                show_error("Utilisateurs", str(exc))

        btns = ctk.CTkFrame(dlg, fg_color="transparent")
        btns.pack(fill="x", padx=24, pady=20)
        PrimaryButton(btns, text=" Enregistrer", icon="check", command=save).pack(side="right")
        GhostButton(btns, text="Annuler", command=dlg.destroy).pack(side="right", padx=8)

    def _add(self) -> None:
        self._form()

    def _edit(self) -> None:
        uid = self._selected()
        if not uid:
            show_error("Utilisateurs", "Sélectionnez un utilisateur.")
            return
        self._form(self.ctx.auth.get_by_id(uid))

    def _toggle(self) -> None:
        uid = self._selected()
        if not uid:
            show_error("Utilisateurs", "Sélectionnez un utilisateur.")
            return
        user = self.ctx.auth.get_by_id(uid)
        try:
            self.ctx.auth.update_user(uid, active=not user.active)
            self.refresh()
            toast(
                self,
                "Compte activé" if not user.active else "Compte désactivé",
                "success",
            )
        except ValueError as exc:
            show_error("Utilisateurs", str(exc))

    def _delete(self) -> None:
        uid = self._selected()
        if not uid:
            show_error("Utilisateurs", "Sélectionnez un utilisateur.")
            return
        if uid == self.user.id:
            show_error("Utilisateurs", "Vous ne pouvez pas supprimer votre propre compte.")
            return
        if ask_confirm("Supprimer", "Supprimer cet utilisateur ?"):
            try:
                self.ctx.auth.delete_user(uid)
                self.refresh()
                toast(self, "Utilisateur supprimé", "success")
            except ValueError as exc:
                show_error("Utilisateurs", str(exc))
