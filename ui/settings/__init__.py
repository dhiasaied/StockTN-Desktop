from __future__ import annotations

from datetime import datetime

import customtkinter as ctk
from tkinter import filedialog

from models.user import User
from services.app_context import AppContext
from ui import COLORS, FONT_FAMILY, RADIUS
from ui.common import (
    DangerButton,
    DataTable,
    GhostButton,
    PageHeader,
    PrimaryButton,
    SuccessButton,
    ask_confirm,
    show_error,
    show_info,
    toast,
)

class SettingsView(ctk.CTkFrame):
    def __init__(self, master, ctx: AppContext, user: User):
        super().__init__(master, fg_color=COLORS["bg"])
        self.ctx = ctx
        self.user = user
        self._build()
        self.refresh()

    def _build(self) -> None:
        PageHeader(
            self, "Sauvegarde & restauration",
            "Protection des fichiers JSON locaux",
            icon="settings",
        ).pack(fill="x", padx=28, pady=(22, 14))

        info = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        info.pack(fill="x", padx=28, pady=(0, 12))
        ctk.CTkLabel(
            info,
            text=(
                "Les sauvegardes compressent tous les fichiers data/*.json.\n"
                "Une restauration remplace les données actuelles "
                "(une copie de sécurité PreRestore est créée automatiquement)."
            ),
            text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            justify="left",
            anchor="w",
        ).pack(fill="x", padx=16, pady=14)

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=28, pady=(0, 10))
        SuccessButton(
            toolbar, text=" Créer une sauvegarde", icon="plus", height=40,
            command=self._backup,
        ).pack(side="left")
        PrimaryButton(
            toolbar, text=" Restaurer la sélection", icon="check", height=40,
            command=self._restore,
        ).pack(side="left", padx=8)
        GhostButton(
            toolbar, text=" Importer un .zip", height=40, command=self._import
        ).pack(side="left")
        DangerButton(
            toolbar, text=" Supprimer", height=40, command=self._delete
        ).pack(side="right")

        self.table = DataTable(
            self,
            [
                ("name", "Fichier", 280),
                ("date", "Date", 180),
                ("size", "Taille", 100),
            ],
            empty_title="Aucune sauvegarde",
            empty_message="Créez une sauvegarde pour protéger vos données.",
        )
        self.table.pack(fill="both", expand=True, padx=28, pady=(0, 24))

    def refresh(self) -> None:
        backups = self.ctx.backup.list_backups()
        rows, iids = [], []
        for b in backups:
            size_kb = b.stat().st_size / 1024
            mtime = datetime.fromtimestamp(b.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            rows.append((b.name, mtime, f"{size_kb:.1f} Ko"))
            iids.append(str(b))
        self.table.set_rows(rows, iids)

    def _backup(self) -> None:
        try:
            path = self.ctx.backup.create_backup()
            show_info("Sauvegarde", f"Sauvegarde créée :\n{path.name}")
            toast(self, "Sauvegarde créée", "success")
            self.refresh()
        except Exception as exc:
            show_error("Sauvegarde", str(exc))

    def _restore(self) -> None:
        iid = self.table.get_selected()
        if not iid:
            show_error("Restauration", "Sélectionnez une sauvegarde.")
            return
        if not ask_confirm(
            "Restauration",
            "Restaurer cette sauvegarde ? Les données actuelles seront remplacées.",
        ):
            return
        try:
            self.ctx.backup.restore_backup(iid)
            show_info(
                "Restauration",
                "Données restaurées. Redémarrez l'application pour recharger complètement.",
            )
            toast(self, "Données restaurées", "success")
            self.refresh()
        except Exception as exc:
            show_error("Restauration", str(exc))

    def _import(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Archive ZIP", "*.zip")])
        if not path:
            return
        if not ask_confirm("Import", "Restaurer depuis ce fichier ?"):
            return
        try:
            self.ctx.backup.restore_backup(path)
            show_info("Import", "Restauration terminée.")
            toast(self, "Import terminé", "success")
            self.refresh()
        except Exception as exc:
            show_error("Import", str(exc))

    def _delete(self) -> None:
        iid = self.table.get_selected()
        if not iid:
            show_error("Sauvegarde", "Sélectionnez une sauvegarde.")
            return
        if ask_confirm("Supprimer", "Supprimer cette sauvegarde ?"):
            try:
                self.ctx.backup.delete_backup(iid)
                self.refresh()
                toast(self, "Sauvegarde supprimée", "success")
            except Exception as exc:
                show_error("Sauvegarde", str(exc))
