from __future__ import annotations

import customtkinter as ctk

from services.app_context import AppContext
from ui import COLORS, FONT_FAMILY, RADIUS
from ui.common import PrimaryButton, show_error, styled_entry, toast
from ui.icons import get_icon
from utils.images import load_logo

class LoginView(ctk.CTkFrame):
    def __init__(self, master, ctx: AppContext, on_success):
        super().__init__(master, fg_color=COLORS["bg"])
        self.ctx = ctx
        self.on_success = on_success
        self._build()
        self.after(80, self._animate_in)

    def _build(self) -> None:
        # Panneau gauche — brand
        self.left = ctk.CTkFrame(self, fg_color=COLORS["sidebar"], corner_radius=0)
        self.left.place(relx=0, rely=0, relwidth=0.42, relheight=1)

        # Dégradé simulé (bande accent)
        accent_strip = ctk.CTkFrame(
            self.left, fg_color=COLORS["primary"], width=4, corner_radius=0
        )
        accent_strip.place(relx=1.0, rely=0, relheight=1, anchor="ne")

        brand = ctk.CTkFrame(self.left, fg_color="transparent")
        brand.place(relx=0.5, rely=0.45, anchor="center")

        logo = load_logo((128, 128))
        if logo:
            ctk.CTkLabel(brand, text="", image=logo).pack(pady=(0, 18))
            self._logo_ref = logo

        ctk.CTkLabel(
            brand,
            text="StockTN",
            font=ctk.CTkFont(family=FONT_FAMILY, size=40, weight="bold"),
            text_color="white",
        ).pack()
        ctk.CTkLabel(
            brand,
            text="Desktop",
            font=ctk.CTkFont(family=FONT_FAMILY, size=16),
            text_color=COLORS["primary_light"],
        ).pack(pady=(0, 18))
        ctk.CTkLabel(
            brand,
            text="Gestion de stock professionnelle\npour le commerce en Tunisie",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            text_color=COLORS["sidebar_text"],
            justify="center",
        ).pack()

        # Features hints
        features = ctk.CTkFrame(self.left, fg_color="transparent")
        features.place(relx=0.5, rely=0.82, anchor="center")
        for text, icon in (
            ("Stock & alertes", "warehouse"),
            ("Caisse & ventes", "shopping-cart"),
            ("Rapports exportables", "bar-chart-3"),
        ):
            row = ctk.CTkFrame(features, fg_color="transparent")
            row.pack(anchor="w", pady=4)
            img = get_icon(icon, 14, COLORS["primary_light"])
            ctk.CTkLabel(row, text="", image=img).pack(side="left", padx=(0, 8))
            if not hasattr(self, "_feat_icons"):
                self._feat_icons = []
            self._feat_icons.append(img)
            ctk.CTkLabel(
                row,
                text=text,
                font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                text_color=COLORS["sidebar_text"],
            ).pack(side="left")

        # Carte connexion
        self.card = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["xl"],
            width=440,
            height=500,
            border_width=1,
            border_color=COLORS["border"],
        )
        self.card.place(relx=0.68, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        inner = ctk.CTkFrame(self.card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=40, pady=40)

        lock = get_icon("lock", 22, COLORS["primary"])
        lock_badge = ctk.CTkFrame(
            inner,
            fg_color=COLORS["primary_soft"],
            width=44,
            height=44,
            corner_radius=RADIUS["md"],
        )
        lock_badge.pack(anchor="w", pady=(0, 16))
        lock_badge.pack_propagate(False)
        ctk.CTkLabel(lock_badge, text="", image=lock).place(relx=0.5, rely=0.5, anchor="center")
        self._lock_ref = lock

        ctk.CTkLabel(
            inner,
            text="Connexion",
            font=ctk.CTkFont(family=FONT_FAMILY, size=26, weight="bold"),
            text_color=COLORS["text"],
            anchor="w",
        ).pack(fill="x")
        ctk.CTkLabel(
            inner,
            text="Accédez à votre espace StockTN",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            text_color=COLORS["text_muted"],
            anchor="w",
        ).pack(fill="x", pady=(4, 28))

        ctk.CTkLabel(
            inner,
            text="Nom d'utilisateur",
            anchor="w",
            text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        ).pack(fill="x")
        self.username = styled_entry(inner, placeholder_text="ex: admin")
        self.username.pack(fill="x", pady=(6, 16))

        ctk.CTkLabel(
            inner,
            text="Mot de passe",
            anchor="w",
            text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        ).pack(fill="x")
        self.password = styled_entry(inner, show="•", placeholder_text="••••••••")
        self.password.pack(fill="x", pady=(6, 8))
        self.password.bind("<Return>", lambda e: self._login())

        self.hint = ctk.CTkLabel(
            inner,
            text="Comptes démo : admin / vendeur / client\nMot de passe : admin123 / vendeur123 / client123",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLORS["text_muted"],
            justify="left",
            anchor="w",
        )
        self.hint.pack(fill="x", pady=(12, 22))

        self.login_btn = PrimaryButton(
            inner,
            text="  Se connecter",
            icon="check",
            height=46,
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            command=self._login,
        )
        self.login_btn.pack(fill="x")

        self.username.insert(0, "admin")
        self.username.focus()

    def _animate_in(self) -> None:
        try:
            if self.card.winfo_exists():
                self.card.configure(border_color=COLORS["primary_light"])
                self.after(
                    220,
                    lambda: self.card.winfo_exists()
                    and self.card.configure(border_color=COLORS["border"]),
                )
        except Exception:
            pass

    def _login(self) -> None:
        self.login_btn.configure(state="disabled", text="  Connexion…")
        self.update_idletasks()
        try:
            user = self.ctx.auth.login(
                self.username.get().strip(),
                self.password.get(),
            )
            self.ctx.current_user = user
            toast(self, f"Bienvenue, {user.full_name}", "success")
            self.after(200, lambda: self.on_success(user))
        except ValueError as exc:
            self.login_btn.configure(state="normal", text="  Se connecter")
            show_error("Connexion", str(exc))
            toast(self, str(exc), "error")
