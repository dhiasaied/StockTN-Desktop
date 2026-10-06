from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox, ttk
from typing import Callable, Optional, Sequence

from ui import COLORS, FONT_FAMILY, RADIUS
from ui.icons import ACTION_ICONS, NAV_ICONS, get_icon

# ─── Messages (dialogs natifs, conservés pour compatibilité) ───────────────

def show_error(title: str, message: str) -> None:
    messagebox.showerror(title, message)

def show_info(title: str, message: str) -> None:
    messagebox.showinfo(title, message)

def show_warning(title: str, message: str) -> None:
    messagebox.showwarning(title, message)

def ask_confirm(title: str, message: str) -> bool:
    return messagebox.askyesno(title, message)

# ─── Animations subtiles ────────────────────────────────────────────────────

def fade_in(widget, steps: int = 6, delay: int = 16) -> None:
    try:
        widget.update_idletasks()
    except Exception:
        return

    # Micro-délai pour permettre le rendu puis animer la géométrie
    def _pulse(step=0):
        if not widget.winfo_exists():
            return
        # Léger scale via padx/pady n'est pas fiable ; on anime juste un highlight
        if step >= steps:
            return
        widget.after(delay, lambda: _pulse(step + 1))

    widget.after(delay, _pulse)

def stagger_pack(widgets: list, master_after, base_delay: int = 40) -> None:
    for i, w in enumerate(widgets):
        try:
            w.configure(fg_color=COLORS["bg"])  # may fail for some
        except Exception:
            pass

        def show(widget=w, idx=i):
            if not widget.winfo_exists():
                return
            try:
                # Restore intended surface if it has _target_fg
                target = getattr(widget, "_target_fg", None)
                if target is not None:
                    widget.configure(fg_color=target)
            except Exception:
                pass

        master_after.after(base_delay * (i + 1), show)

def animate_value_label(label, end_text: str, duration_ms: int = 280) -> None:
    if not label.winfo_exists():
        return
    label.configure(text="")
    steps = 5
    delay = max(20, duration_ms // steps)

    def step(i=0):
        if not label.winfo_exists():
            return
        if i >= steps:
            label.configure(text=end_text)
            return
        # Progressive reveal of characters for numeric feel
        n = max(1, int(len(end_text) * (i + 1) / steps))
        label.configure(text=end_text[:n])
        label.after(delay, lambda: step(i + 1))

    label.after(30, step)

# ─── Toast notifications ───────────────────────────────────────────────────

class ToastManager:

    def __init__(self):
        self._active: list = []

    def show(self, root, message: str, kind: str = "info", duration: int = 2800) -> None:
        colors = {
            "success": (COLORS["success"], COLORS["success_soft"], "check-circle"),
            "error": (COLORS["danger"], COLORS["danger_soft"], "x-circle"),
            "warning": (COLORS["warning"], COLORS["warning_soft"], "alert-triangle"),
            "info": (COLORS["info"], COLORS["info_soft"], "bell"),
        }
        accent, bg, icon_name = colors.get(kind, colors["info"])

        toast = ctk.CTkFrame(
            root,
            fg_color=bg,
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        icon = get_icon(icon_name, 18, accent)
        inner = ctk.CTkFrame(toast, fg_color="transparent")
        inner.pack(padx=14, pady=10)
        ctk.CTkLabel(inner, text="", image=icon).pack(side="left", padx=(0, 10))
        toast._icon_ref = icon
        ctk.CTkLabel(
            inner,
            text=message,
            text_color=COLORS["text"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            wraplength=320,
            justify="left",
        ).pack(side="left")

        # Barre accent à gauche
        bar = ctk.CTkFrame(toast, fg_color=accent, width=4, corner_radius=2)
        bar.place(x=0, y=4, relheight=0.85)

        offset = 24 + len(self._active) * 72
        toast.place(relx=1.0, rely=1.0, x=-24, y=-offset, anchor="se")
        self._active.append(toast)

        def dismiss():
            if toast in self._active:
                self._active.remove(toast)
            if toast.winfo_exists():
                toast.destroy()
            self._reposition(root)

        toast.after(duration, dismiss)
        toast.bind("<Button-1>", lambda e: dismiss())

    def _reposition(self, root) -> None:
        for i, t in enumerate(self._active):
            if t.winfo_exists():
                t.place(relx=1.0, rely=1.0, x=-24, y=-(24 + i * 72), anchor="se")

_toasts = ToastManager()

def toast(widget, message: str, kind: str = "info") -> None:
    root = widget.winfo_toplevel()
    _toasts.show(root, message, kind)

# ─── Boutons stylisés ───────────────────────────────────────────────────────

def _btn_base(kwargs: dict) -> dict:
    defaults = {
        "height": 38,
        "corner_radius": RADIUS["sm"],
        "font": ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
        "border_width": 0,
    }
    defaults.update(kwargs)
    return defaults

class PrimaryButton(ctk.CTkButton):
    def __init__(self, master, text: str = "", icon: str | None = None, **kwargs):
        img = get_icon(icon, 16, "#FFFFFF") if icon else None
        Kw = _btn_base({
            "fg_color": COLORS["primary"],
            "hover_color": COLORS["primary_dark"],
            "text_color": "#FFFFFF",
            "image": img,
            "compound": "left",
            "anchor": "center",
        })
        Kw.update(kwargs)
        super().__init__(master, text=text, **Kw)
        if img:
            self._icon_ref = img

class SuccessButton(ctk.CTkButton):
    def __init__(self, master, text: str = "", icon: str = "plus", **kwargs):
        img = get_icon(icon, 16, "#FFFFFF") if icon else None
        Kw = _btn_base({
            "fg_color": COLORS["success"],
            "hover_color": "#047857",
            "text_color": "#FFFFFF",
            "image": img,
            "compound": "left",
        })
        Kw.update(kwargs)
        super().__init__(master, text=text, **Kw)
        if img:
            self._icon_ref = img

class DangerButton(ctk.CTkButton):
    def __init__(self, master, text: str = "", icon: str = "trash-2", **kwargs):
        img = get_icon(icon, 16, "#FFFFFF") if icon else None
        Kw = _btn_base({
            "fg_color": COLORS["danger"],
            "hover_color": "#B91C1C",
            "text_color": "#FFFFFF",
            "image": img,
            "compound": "left",
        })
        Kw.update(kwargs)
        super().__init__(master, text=text, **Kw)
        if img:
            self._icon_ref = img

class SecondaryButton(ctk.CTkButton):
    def __init__(self, master, text: str = "", icon: str | None = None, **kwargs):
        img = get_icon(icon, 16, COLORS["primary"]) if icon else None
        Kw = _btn_base({
            "fg_color": COLORS["primary_soft"],
            "hover_color": "#99F6E4",
            "text_color": COLORS["primary_dark"],
            "image": img,
            "compound": "left",
        })
        Kw.update(kwargs)
        super().__init__(master, text=text, **Kw)
        if img:
            self._icon_ref = img

class GhostButton(ctk.CTkButton):
    def __init__(self, master, text: str = "", icon: str | None = None, **kwargs):
        img = get_icon(icon, 16, COLORS["text_muted"]) if icon else None
        Kw = _btn_base({
            "fg_color": "transparent",
            "hover_color": COLORS["surface_hover"],
            "text_color": COLORS["text_secondary"],
            "border_width": 1,
            "border_color": COLORS["border"],
            "image": img,
            "compound": "left",
            "font": ctk.CTkFont(family=FONT_FAMILY, size=13),
        })
        Kw.update(kwargs)
        super().__init__(master, text=text, **Kw)
        if img:
            self._icon_ref = img

class WarningButton(ctk.CTkButton):
    def __init__(self, master, text: str = "", icon: str | None = None, **kwargs):
        img = get_icon(icon, 16, "#FFFFFF") if icon else None
        Kw = _btn_base({
            "fg_color": COLORS["warning"],
            "hover_color": "#B45309",
            "text_color": "#FFFFFF",
            "image": img,
            "compound": "left",
        })
        Kw.update(kwargs)
        super().__init__(master, text=text, **Kw)
        if img:
            self._icon_ref = img

# ─── Champs de formulaire ───────────────────────────────────────────────────

def styled_entry(master, **kwargs) -> ctk.CTkEntry:
    defaults = {
        "height": 40,
        "corner_radius": RADIUS["sm"],
        "border_color": COLORS["border"],
        "fg_color": COLORS["input_bg"],
        "text_color": COLORS["text"],
        "placeholder_text_color": COLORS["text_muted"],
        "font": ctk.CTkFont(family=FONT_FAMILY, size=13),
        "border_width": 1,
    }
    defaults.update(kwargs)
    entry = ctk.CTkEntry(master, **defaults)

    def on_focus_in(_e=None):
        entry.configure(border_color=COLORS["primary"])

    def on_focus_out(_e=None):
        entry.configure(border_color=COLORS["border"])

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    return entry

def styled_combo(master, **kwargs) -> ctk.CTkComboBox:
    defaults = {
        "height": 40,
        "corner_radius": RADIUS["sm"],
        "border_color": COLORS["border"],
        "fg_color": COLORS["input_bg"],
        "button_color": COLORS["primary"],
        "button_hover_color": COLORS["primary_dark"],
        "dropdown_fg_color": COLORS["surface"],
        "dropdown_hover_color": COLORS["primary_soft"],
        "text_color": COLORS["text"],
        "font": ctk.CTkFont(family=FONT_FAMILY, size=13),
        "border_width": 1,
    }
    defaults.update(kwargs)
    return ctk.CTkComboBox(master, **defaults)

# ─── En-tête de page ────────────────────────────────────────────────────────

class PageHeader(ctk.CTkFrame):
    def __init__(
        self,
        master,
        title: str,
        subtitle: str = "",
        icon: str | None = None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x")

        if icon:
            icon_key = NAV_ICONS.get(icon, icon)
            img = get_icon(icon_key, 28, COLORS["primary"])
            badge = ctk.CTkFrame(
                row,
                fg_color=COLORS["primary_soft"],
                width=48,
                height=48,
                corner_radius=RADIUS["md"],
            )
            badge.pack(side="left", padx=(0, 14))
            badge.pack_propagate(False)
            lbl = ctk.CTkLabel(badge, text="", image=img)
            lbl.place(relx=0.5, rely=0.5, anchor="center")
            self._icon_ref = img

        text_col = ctk.CTkFrame(row, fg_color="transparent")
        text_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            text_col,
            text=title,
            font=ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold"),
            text_color=COLORS["text"],
            anchor="w",
        ).pack(fill="x")
        if subtitle:
            ctk.CTkLabel(
                text_col,
                text=subtitle,
                font=ctk.CTkFont(family=FONT_FAMILY, size=13),
                text_color=COLORS["text_muted"],
                anchor="w",
            ).pack(fill="x", pady=(2, 0))

# ─── Carte statistique ──────────────────────────────────────────────────────

class StatCard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        title: str,
        value: str,
        subtitle: str = "",
        accent: str = COLORS["primary"],
        icon: str | None = None,
        animate: bool = True,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self._target_fg = COLORS["surface"]
        self._accent = accent

        # Accent top bar
        bar = ctk.CTkFrame(self, fg_color=accent, height=3, corner_radius=0)
        bar.pack(fill="x", side="top")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=(14, 16))

        top = ctk.CTkFrame(body, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(
            top,
            text=title,
            text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        if icon:
            icon_key = NAV_ICONS.get(icon, ACTION_ICONS.get(icon, icon))
            img = get_icon(icon_key, 18, accent)
            icon_badge = ctk.CTkFrame(
                top,
                fg_color=self._soft_bg(accent),
                width=34,
                height=34,
                corner_radius=RADIUS["sm"],
            )
            icon_badge.pack(side="right")
            icon_badge.pack_propagate(False)
            il = ctk.CTkLabel(icon_badge, text="", image=img)
            il.place(relx=0.5, rely=0.5, anchor="center")
            self._icon_ref = img

        self.value_label = ctk.CTkLabel(
            body,
            text=value if not animate else "",
            text_color=COLORS["text"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=26, weight="bold"),
            anchor="w",
        )
        self.value_label.pack(fill="x", pady=(8, 0))

        if subtitle:
            ctk.CTkLabel(
                body,
                text=subtitle,
                text_color=COLORS["text_muted"],
                font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                anchor="w",
            ).pack(fill="x", pady=(2, 0))

        # Hover micro-interaction
        for w in (self, body, top):
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)

        if animate:
            animate_value_label(self.value_label, value)

    @staticmethod
    def _soft_bg(accent: str) -> str:
        mapping = {
            COLORS["primary"]: COLORS["primary_soft"],
            COLORS["primary_light"]: COLORS["primary_soft"],
            COLORS["success"]: COLORS["success_soft"],
            COLORS["warning"]: COLORS["warning_soft"],
            COLORS["danger"]: COLORS["danger_soft"],
            COLORS["info"]: COLORS["info_soft"],
        }
        return mapping.get(accent, COLORS["primary_soft"])

    def _on_enter(self, _e=None):
        try:
            self.configure(border_color=self._accent)
        except Exception:
            pass

    def _on_leave(self, _e=None):
        try:
            self.configure(border_color=COLORS["border"])
        except Exception:
            pass

    def set_value(self, value: str) -> None:
        animate_value_label(self.value_label, value)

# ─── Carte de contenu ───────────────────────────────────────────────────────

class ContentCard(ctk.CTkFrame):
    def __init__(self, master, title: str = "", icon: str | None = None, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        if title:
            hdr = ctk.CTkFrame(self, fg_color="transparent")
            hdr.pack(fill="x", padx=16, pady=(14, 4))
            if icon:
                img = get_icon(NAV_ICONS.get(icon, ACTION_ICONS.get(icon, icon)), 16, COLORS["primary"])
                ctk.CTkLabel(hdr, text="", image=img).pack(side="left", padx=(0, 8))
                self._hdr_icon = img
            ctk.CTkLabel(
                hdr,
                text=title,
                font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
                text_color=COLORS["text"],
                anchor="w",
            ).pack(side="left")

# ─── États vides / loading / erreur ─────────────────────────────────────────

class EmptyState(ctk.CTkFrame):
    def __init__(
        self,
        master,
        title: str = "Aucune donnée",
        message: str = "Il n'y a rien à afficher pour le moment.",
        icon: str = "inbox",
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        img = get_icon(icon, 40, COLORS["text_muted"])
        badge = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface_hover"],
            width=72,
            height=72,
            corner_radius=RADIUS["lg"],
        )
        badge.pack(pady=(24, 12))
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text="", image=img).place(relx=0.5, rely=0.5, anchor="center")
        self._icon_ref = img
        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            text_color=COLORS["text"],
        ).pack()
        ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLORS["text_muted"],
            wraplength=360,
            justify="center",
        ).pack(pady=(4, 24))

class LoadingOverlay(ctk.CTkFrame):
    def __init__(self, master, text: str = "Chargement…", **kwargs):
        super().__init__(master, fg_color=COLORS["bg"], **kwargs)
        img = get_icon("loader", 28, COLORS["primary"])
        ctk.CTkLabel(self, text="", image=img).pack(pady=(40, 8))
        self._icon_ref = img
        ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            text_color=COLORS["text_muted"],
        ).pack()
        self._angle = 0
        self._spin()

    def _spin(self):
        if not self.winfo_exists():
            return
        # Recréer l'icône avec une teinte pulsante
        shade = COLORS["primary"] if self._angle % 2 == 0 else COLORS["primary_light"]
        img = get_icon("loader", 28, shade)
        for child in self.winfo_children():
            if isinstance(child, ctk.CTkLabel) and child.cget("text") == "":
                child.configure(image=img)
                self._icon_ref = img
                break
        self._angle += 1
        self.after(400, self._spin)

class StatusBanner(ctk.CTkFrame):

    def __init__(self, master, message: str, kind: str = "info", **kwargs):
        palette = {
            "success": (COLORS["success_soft"], COLORS["success"], "check-circle"),
            "error": (COLORS["danger_soft"], COLORS["danger"], "x-circle"),
            "warning": (COLORS["warning_soft"], COLORS["warning"], "alert-triangle"),
            "info": (COLORS["info_soft"], COLORS["info"], "bell"),
        }
        bg, fg, icon = palette.get(kind, palette["info"])
        super().__init__(
            master,
            fg_color=bg,
            corner_radius=RADIUS["sm"],
            border_width=1,
            border_color=fg,
            **kwargs,
        )
        img = get_icon(icon, 16, fg)
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=10)
        ctk.CTkLabel(row, text="", image=img).pack(side="left", padx=(0, 8))
        self._icon_ref = img
        ctk.CTkLabel(
            row,
            text=message,
            text_color=COLORS["text"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            anchor="w",
            justify="left",
        ).pack(side="left", fill="x", expand=True)

# ─── Barre d'outils ─────────────────────────────────────────────────────────

class Toolbar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

# ─── Tableaux ───────────────────────────────────────────────────────────────

def setup_treeview_style() -> None:
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure(
        "StockTN.Treeview",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        fieldbackground=COLORS["surface"],
        rowheight=36,
        borderwidth=0,
        font=(FONT_FAMILY, 10),
    )
    style.configure(
        "StockTN.Treeview.Heading",
        background=COLORS["sidebar"],
        foreground="white",
        relief="flat",
        font=(FONT_FAMILY, 10, "bold"),
        padding=6,
    )
    style.map(
        "StockTN.Treeview",
        background=[("selected", COLORS["primary_soft"])],
        foreground=[("selected", COLORS["primary_dark"])],
    )
    style.map(
        "StockTN.Treeview.Heading",
        background=[("active", COLORS["primary"])],
    )

class DataTable(ctk.CTkFrame):

    def __init__(
        self,
        master,
        columns: Sequence[tuple[str, str, int]],
        on_select: Optional[Callable] = None,
        empty_title: str = "Aucune donnée",
        empty_message: str = "Aucun élément à afficher.",
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        setup_treeview_style()
        self.columns = columns
        self._empty_title = empty_title
        self._empty_message = empty_message

        self._table_container = ctk.CTkFrame(self, fg_color="transparent")
        self._table_container.pack(fill="both", expand=True)

        ids = [c[0] for c in columns]
        self.tree = ttk.Treeview(
            self._table_container,
            columns=ids,
            show="headings",
            style="StockTN.Treeview",
            selectmode="browse",
        )
        for col_id, heading, width in columns:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width, minwidth=60, anchor="w")

        vsb = ttk.Scrollbar(self._table_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self._table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=(10, 0))
        vsb.grid(row=0, column=1, sticky="ns", pady=10, padx=(0, 10))
        hsb.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        self._table_container.grid_rowconfigure(0, weight=1)
        self._table_container.grid_columnconfigure(0, weight=1)

        self._empty = EmptyState(
            self, title=empty_title, message=empty_message, icon="inbox"
        )

        if on_select:
            self.tree.bind("<<TreeviewSelect>>", lambda e: on_select(self.get_selected()))

        # Alternance de lignes
        self.tree.tag_configure("odd", background="#F8FAFC")
        self.tree.tag_configure("even", background=COLORS["surface"])

    def clear(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

    def set_rows(self, rows: Sequence[Sequence], iids: Optional[Sequence] = None) -> None:
        self.clear()
        if not rows:
            self._table_container.pack_forget()
            self._empty.pack(fill="both", expand=True)
            return
        self._empty.pack_forget()
        self._table_container.pack(fill="both", expand=True)
        for idx, row in enumerate(rows):
            iid = str(iids[idx]) if iids is not None else str(idx)
            tag = "odd" if idx % 2 else "even"
            self.tree.insert("", "end", iid=iid, values=list(row), tags=(tag,))

    def get_selected(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return sel[0]

    def get_selected_values(self):
        iid = self.get_selected()
        if iid is None:
            return None
        return self.tree.item(iid, "values")

# ─── Dialogue formulaire stylisé ────────────────────────────────────────────

def style_dialog(dlg: ctk.CTkToplevel, title: str, size: str = "460x480") -> None:
    dlg.title(title)
    dlg.geometry(size)
    dlg.configure(fg_color=COLORS["bg"])
    dlg.grab_set()
    try:
        dlg.attributes("-topmost", True)
        dlg.after(50, lambda: dlg.attributes("-topmost", False))
    except Exception:
        pass
