#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

# Garantit que le dossier StockTN est dans le path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import customtkinter as ctk

from services.app_context import AppContext
from ui import COLORS
from ui.login import LoginView
from ui.main_window import MainWindow
from utils.images import LOGO_PATH

class StockTNApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("StockTN Desktop")
        self.geometry("1280x800")
        self.minsize(1024, 680)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        self.configure(fg_color=COLORS["bg"])

        if LOGO_PATH.exists():
            try:
                from PIL import Image, ImageTk
                icon = ImageTk.PhotoImage(Image.open(LOGO_PATH))
                self.iconphoto(True, icon)
                self._icon_ref = icon
            except Exception:
                pass

        self.ctx = AppContext(ROOT)
        self._container = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        self._container.pack(fill="both", expand=True)
        self.show_login()

        # Centrer la fenêtre
        self.update_idletasks()
        w, h = 1280, 800
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _clear(self) -> None:
        for child in self._container.winfo_children():
            child.destroy()

    def show_login(self) -> None:
        self.ctx.current_user = None
        self._clear()
        LoginView(self._container, self.ctx, on_success=self.show_main).pack(
            fill="both", expand=True
        )

    def show_main(self, user) -> None:
        self._clear()
        MainWindow(
            self._container, self.ctx, user, on_logout=self.show_login
        ).pack(fill="both", expand=True)

def main() -> None:
    app = StockTNApp()
    app.mainloop()

if __name__ == "__main__":
    main()
