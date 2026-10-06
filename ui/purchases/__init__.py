from __future__ import annotations

import customtkinter as ctk

from models.user import User
from services.app_context import AppContext
from ui import COLORS, FONT_FAMILY, RADIUS
from ui.common import (
    DangerButton,
    DataTable,
    PageHeader,
    PrimaryButton,
    SuccessButton,
    show_error,
    styled_combo,
    styled_entry,
    toast,
)
from utils.validators import format_tnd

class PurchasesView(ctk.CTkFrame):
    def __init__(self, master, ctx: AppContext, user: User):
        super().__init__(master, fg_color=COLORS["bg"])
        self.ctx = ctx
        self.user = user
        self.items: list[dict] = []
        self._build()
        self.refresh()

    def _build(self) -> None:
        PageHeader(
            self, "Achats", "Réapprovisionnement fournisseurs", icon="purchases"
        ).pack(fill="x", padx=28, pady=(22, 14))
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
        form = tabs.add("Nouvel achat")
        hist = tabs.add("Historique")

        top = ctk.CTkFrame(
            form,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        top.pack(fill="x", padx=8, pady=8)
        ctk.CTkLabel(
            top, text="Fournisseur", text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        ).grid(row=0, column=0, padx=14, pady=10, sticky="w")
        suppliers = [f"{s.id} - {s.name}" for s in self.ctx.suppliers.get_all()]
        self.supplier_box = styled_combo(top, values=suppliers or ["—"], width=280)
        if suppliers:
            self.supplier_box.set(suppliers[0])
        self.supplier_box.grid(row=0, column=1, padx=8, pady=10)

        ctk.CTkLabel(
            top, text="Produit", text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        ).grid(row=1, column=0, padx=14, pady=10, sticky="w")
        products = [f"{p.id} - {p.name}" for p in self.ctx.products.get_all()]
        self.product_box = styled_combo(top, values=products or ["—"], width=280)
        if products:
            self.product_box.set(products[0])
        self.product_box.grid(row=1, column=1, padx=8, pady=10)

        ctk.CTkLabel(
            top, text="Quantité", text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        ).grid(row=1, column=2, padx=8, pady=10)
        self.qty_entry = styled_entry(top, width=80)
        self.qty_entry.insert(0, "1")
        self.qty_entry.grid(row=1, column=3, padx=4, pady=10)

        ctk.CTkLabel(
            top, text="Prix achat", text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        ).grid(row=1, column=4, padx=8, pady=10)
        self.price_entry = styled_entry(top, width=100)
        self.price_entry.grid(row=1, column=5, padx=4, pady=10)

        PrimaryButton(
            top, text=" Ajouter ligne", icon="plus", command=self._add_line
        ).grid(row=1, column=6, padx=12, pady=10)

        self.lines_table = DataTable(
            form,
            [
                ("product", "Produit", 220),
                ("qty", "Qté", 80),
                ("price", "P.U.", 100),
                ("total", "Total", 120),
            ],
            empty_title="Aucune ligne",
            empty_message="Ajoutez des lignes d'achat ci-dessus.",
        )
        self.lines_table.pack(fill="both", expand=True, padx=8, pady=8)

        bottom = ctk.CTkFrame(form, fg_color="transparent")
        bottom.pack(fill="x", padx=8, pady=8)
        self.total_label = ctk.CTkLabel(
            bottom, text="Total : 0.000 TND",
            font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
            text_color=COLORS["primary"],
        )
        self.total_label.pack(side="left")
        SuccessButton(
            bottom, text=" Valider l'achat", icon="check", height=40, command=self._validate
        ).pack(side="right")
        DangerButton(
            bottom, text=" Retirer ligne", width=130, command=self._remove_line
        ).pack(side="right", padx=8)

        self.history = DataTable(
            hist,
            [
                ("id", "N°", 60),
                ("date", "Date", 150),
                ("supplier", "Fournisseur", 200),
                ("user", "Utilisateur", 100),
                ("total", "Total", 120),
            ],
            empty_title="Aucun achat",
            empty_message="Les achats validés apparaîtront ici.",
        )
        self.history.pack(fill="both", expand=True, padx=8, pady=8)

    def _add_line(self) -> None:
        sel = self.product_box.get()
        if " - " not in sel:
            return
        pid = int(sel.split(" - ", 1)[0])
        product = self.ctx.products.get_by_id(pid)
        if not product:
            return
        try:
            qty = int(self.qty_entry.get())
            price = float(self.price_entry.get() or product.purchase_price)
            if qty <= 0 or price < 0:
                raise ValueError
        except ValueError:
            show_error("Achats", "Quantité / prix invalides.")
            return
        self.items.append(
            {
                "product_id": pid,
                "name": product.name,
                "quantity": qty,
                "unit_price": price,
            }
        )
        self._refresh_lines()

    def _refresh_lines(self) -> None:
        rows, iids, total = [], [], 0.0
        for i, item in enumerate(self.items):
            line = item["quantity"] * item["unit_price"]
            total += line
            rows.append((item["name"], item["quantity"], f"{item['unit_price']:.3f}", f"{line:.3f}"))
            iids.append(i)
        self.lines_table.set_rows(rows, iids)
        self.total_label.configure(text=f"Total : {format_tnd(total)}")

    def _remove_line(self) -> None:
        iid = self.lines_table.get_selected()
        if iid is None:
            return
        del self.items[int(iid)]
        self._refresh_lines()

    def _validate(self) -> None:
        sel = self.supplier_box.get()
        if " - " not in sel:
            show_error("Achats", "Sélectionnez un fournisseur.")
            return
        supplier_id = int(sel.split(" - ", 1)[0])
        try:
            purchase = self.ctx.purchases.create_purchase(
                supplier_id=supplier_id,
                items=self.items,
                user=self.user,
            )
            self.items.clear()
            self._refresh_lines()
            self.refresh()
            toast(self, f"Achat #{purchase.id} enregistré — stock mis à jour", "success")
        except ValueError as exc:
            show_error("Achats", str(exc))

    def refresh(self) -> None:
        purchases = self.ctx.purchases.get_all()
        self.history.set_rows(
            [
                (p.id, p.date, p.supplier_name, p.username, format_tnd(p.total))
                for p in purchases
            ],
            [p.id for p in purchases],
        )
