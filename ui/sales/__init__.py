from __future__ import annotations

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
    show_error,
    show_info,
    styled_combo,
    styled_entry,
    toast,
)
from utils.validators import format_tnd

class SalesView(ctk.CTkFrame):
    def __init__(self, master, ctx: AppContext, user: User):
        super().__init__(master, fg_color=COLORS["bg"])
        self.ctx = ctx
        self.user = user
        self.cart: list[dict] = []
        self._build()
        self._refresh_history()

    def _build(self) -> None:
        PageHeader(self, "Caisse / Ventes", "Point de vente et historique", icon="sales").pack(
            fill="x", padx=28, pady=(22, 14)
        )

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
        pos = tabs.add("Caisse")
        hist = tabs.add("Historique")

        # --- Caisse ---
        left = ctk.CTkFrame(
            pos,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        left.pack(side="left", fill="both", expand=True, padx=(8, 6), pady=8)
        right = ctk.CTkFrame(
            pos,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["md"],
            width=380,
            border_width=1,
            border_color=COLORS["border"],
        )
        right.pack(side="right", fill="y", padx=(6, 8), pady=8)
        right.pack_propagate(False)

        search_row = ctk.CTkFrame(left, fg_color="transparent")
        search_row.pack(fill="x", padx=14, pady=14)
        self.prod_search = styled_entry(
            search_row, placeholder_text="Code, nom ou code-barres…"
        )
        self.prod_search.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.prod_search.bind("<Return>", lambda e: self._add_from_search())
        PrimaryButton(
            search_row, text=" Ajouter", icon="plus", width=110, command=self._add_from_search
        ).pack(side="left")

        self.products_table = DataTable(
            left,
            [
                ("code", "Code", 90),
                ("name", "Produit", 200),
                ("price", "Prix", 100),
                ("qty", "Stock", 70),
            ],
            on_select=lambda _: None,
            empty_title="Aucun produit",
            empty_message="Aucun article disponible en stock.",
        )
        self.products_table.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.products_table.tree.bind("<Double-1>", lambda e: self._add_selected_product())
        self._load_products()

        ctk.CTkLabel(
            right, text="Panier",
            font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=14, pady=(14, 8))

        self.cart_table = DataTable(
            right,
            [
                ("name", "Article", 140),
                ("qty", "Qté", 50),
                ("price", "P.U.", 70),
                ("total", "Total", 80),
            ],
            empty_title="Panier vide",
            empty_message="Ajoutez des articles pour commencer.",
        )
        self.cart_table.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        cust_row = ctk.CTkFrame(right, fg_color="transparent")
        cust_row.pack(fill="x", padx=14, pady=4)
        ctk.CTkLabel(
            cust_row, text="Client", text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        ).pack(anchor="w")
        customers = ["Client comptoir"] + [
            f"{c.id} - {c.full_name}" for c in self.ctx.customers.get_all()
        ]
        self.customer_box = styled_combo(cust_row, values=customers)
        self.customer_box.set("Client comptoir")
        self.customer_box.pack(fill="x")

        pay_row = ctk.CTkFrame(right, fg_color="transparent")
        pay_row.pack(fill="x", padx=14, pady=4)
        ctk.CTkLabel(
            pay_row, text="Paiement", text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        ).pack(anchor="w")
        self.pay_box = styled_combo(
            pay_row, values=["Espèces", "Carte", "Chèque", "Virement"]
        )
        self.pay_box.set("Espèces")
        self.pay_box.pack(fill="x")

        self.total_label = ctk.CTkLabel(
            right, text="Total : 0.000 TND",
            font=ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold"),
            text_color=COLORS["primary"],
        )
        self.total_label.pack(pady=10)

        btn_row = ctk.CTkFrame(right, fg_color="transparent")
        btn_row.pack(fill="x", padx=14, pady=(0, 8))
        DangerButton(
            btn_row, text=" Retirer", width=110, command=self._remove_cart_item
        ).pack(side="left")
        GhostButton(
            btn_row, text="Vider", width=90, command=self._clear_cart
        ).pack(side="left", padx=6)

        SuccessButton(
            right, text=" Valider la vente", icon="check", height=44,
            command=self._checkout,
        ).pack(fill="x", padx=14, pady=(4, 8))
        PrimaryButton(
            right, text=" Imprimer ticket", icon="file-text", height=38,
            command=self._print_last_ticket,
        ).pack(fill="x", padx=14, pady=(0, 14))
        self._last_sale = None

        # --- Historique ---
        self.history_table = DataTable(
            hist,
            [
                ("id", "N°", 60),
                ("date", "Date", 150),
                ("client", "Client", 160),
                ("user", "Vendeur", 100),
                ("pay", "Paiement", 90),
                ("total", "Total", 110),
            ],
            empty_title="Aucune vente",
            empty_message="Les ventes validées apparaîtront ici.",
        )
        self.history_table.pack(fill="both", expand=True, padx=8, pady=8)

    def _load_products(self) -> None:
        products = self.ctx.products.search(availability="available")
        self.products_table.set_rows(
            [
                (p.code, p.name, format_tnd(p.sale_price), p.quantity)
                for p in products
            ],
            [p.id for p in products],
        )

    def _add_from_search(self) -> None:
        q = self.prod_search.get().strip()
        if not q:
            return
        products = self.ctx.products.search(query=q, availability="available")
        if not products:
            show_error("Caisse", "Aucun produit trouvé.")
            return
        self._add_to_cart(products[0].id)
        self.prod_search.delete(0, "end")

    def _add_selected_product(self) -> None:
        iid = self.products_table.get_selected()
        if iid:
            self._add_to_cart(int(iid))

    def _add_to_cart(self, product_id: int) -> None:
        product = self.ctx.products.get_by_id(product_id)
        if not product:
            return
        for item in self.cart:
            if item["product_id"] == product_id:
                if item["quantity"] + 1 > product.quantity:
                    show_error("Caisse", "Stock insuffisant.")
                    return
                item["quantity"] += 1
                self._refresh_cart()
                return
        if product.quantity < 1:
            show_error("Caisse", "Stock insuffisant.")
            return
        self.cart.append(
            {
                "product_id": product.id,
                "name": product.name,
                "quantity": 1,
                "unit_price": product.sale_price,
            }
        )
        self._refresh_cart()

    def _refresh_cart(self) -> None:
        rows, iids = [], []
        total = 0.0
        for idx, item in enumerate(self.cart):
            line = item["quantity"] * item["unit_price"]
            total += line
            rows.append(
                (
                    item["name"],
                    item["quantity"],
                    f"{item['unit_price']:.3f}",
                    f"{line:.3f}",
                )
            )
            iids.append(idx)
        self.cart_table.set_rows(rows, iids)
        self.total_label.configure(text=f"Total : {format_tnd(total)}")

    def _remove_cart_item(self) -> None:
        iid = self.cart_table.get_selected()
        if iid is None:
            return
        del self.cart[int(iid)]
        self._refresh_cart()

    def _clear_cart(self) -> None:
        self.cart.clear()
        self._refresh_cart()

    def _checkout(self) -> None:
        if not self.cart:
            show_error("Caisse", "Le panier est vide.")
            return
        customer_id = None
        customer_name = "Client comptoir"
        sel = self.customer_box.get()
        if sel != "Client comptoir" and " - " in sel:
            customer_id = int(sel.split(" - ", 1)[0])
            customer = self.ctx.customers.get_by_id(customer_id)
            customer_name = customer.full_name if customer else sel

        try:
            sale = self.ctx.sales.create_sale(
                items=self.cart,
                user=self.user,
                customer_id=customer_id,
                customer_name=customer_name,
                payment_method=self.pay_box.get(),
            )
            self._last_sale = sale
            self._clear_cart()
            self._load_products()
            self._refresh_history()
            toast(self, f"Vente #{sale.id} validée — {format_tnd(sale.total)}", "success")
        except ValueError as exc:
            show_error("Caisse", str(exc))

    def _refresh_history(self) -> None:
        sales = self.ctx.sales.get_all()
        self.history_table.set_rows(
            [
                (
                    s.id, s.date, s.customer_name, s.username,
                    s.payment_method, format_tnd(s.total),
                )
                for s in sales
            ],
            [s.id for s in sales],
        )

    def _print_last_ticket(self) -> None:
        sale = self._last_sale
        if not sale:
            iid = self.history_table.get_selected()
            if iid:
                sale = self.ctx.sales.get_by_id(int(iid))
        if not sale:
            show_error("Ticket", "Aucune vente à imprimer.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Ticket texte", "*.txt")],
            initialfile=f"ticket_vente_{sale.id}.txt",
        )
        if not path:
            return
        lines = [
            "=" * 32,
            "      StockTN Desktop",
            "     Ticket de vente",
            "=" * 32,
            f"N° : {sale.id}",
            f"Date : {sale.date}",
            f"Vendeur : {sale.username}",
            f"Client : {sale.customer_name}",
            f"Paiement : {sale.payment_method}",
            "-" * 32,
        ]
        for item in sale.items:
            lines.append(f"{item.product_name}")
            lines.append(
                f"  {item.quantity} x {item.unit_price:.3f} = {item.total:.3f}"
            )
        lines += [
            "-" * 32,
            f"TOTAL : {sale.total:.3f} TND",
            "=" * 32,
            "Merci pour votre achat !",
        ]
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        show_info("Ticket", f"Ticket enregistré :\n{path}")
        toast(self, "Ticket enregistré", "success")
