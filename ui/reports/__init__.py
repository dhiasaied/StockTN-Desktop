from __future__ import annotations

from datetime import datetime

import customtkinter as ctk
from tkinter import filedialog

from models.user import User
from services.app_context import AppContext
from ui import COLORS, FONT_FAMILY
from ui.common import (
    DataTable,
    GhostButton,
    PageHeader,
    PrimaryButton,
    SuccessButton,
    show_error,
    show_info,
    styled_combo,
    toast,
)
from utils.export import export_csv, export_excel, export_pdf
from utils.validators import format_tnd

class ReportsView(ctk.CTkFrame):
    def __init__(self, master, ctx: AppContext, user: User):
        super().__init__(master, fg_color=COLORS["bg"])
        self.ctx = ctx
        self.user = user
        self.current_headers: list[str] = []
        self.current_rows: list[list] = []
        self.current_title = ""
        self._build()

    def _build(self) -> None:
        PageHeader(
            self, "Rapports", "Stock, ventes et achats — export PDF / Excel / CSV",
            icon="reports",
        ).pack(fill="x", padx=28, pady=(22, 14))
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=28, pady=(0, 10))

        self.report_type = styled_combo(
            toolbar,
            values=[
                "Rapport stock",
                "Stock faible / ruptures",
                "Ventes du jour",
                "Ventes de la semaine",
                "Ventes du mois",
                "Achats du jour",
                "Achats du mois",
                "Achats par fournisseur",
            ],
            width=240,
        )
        self.report_type.set("Rapport stock")
        self.report_type.pack(side="left")

        PrimaryButton(
            toolbar, text=" Générer", icon="bar-chart-3", width=120, command=self._generate
        ).pack(side="left", padx=8)
        GhostButton(
            toolbar, text=" Export CSV", width=120, command=lambda: self._export("csv")
        ).pack(side="right", padx=(8, 0))
        SuccessButton(
            toolbar, text=" Export Excel", icon="file-text", width=130,
            command=lambda: self._export("excel"),
        ).pack(side="right", padx=(8, 0))
        PrimaryButton(
            toolbar, text=" Export PDF", icon="file-text", width=120,
            command=lambda: self._export("pdf"),
        ).pack(side="right")

        self.summary = ctk.CTkLabel(
            self, text="", anchor="w", text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
        )
        self.summary.pack(fill="x", padx=28, pady=(0, 6))

        self.table = DataTable(
            self,
            [
                ("c1", "Colonne 1", 140),
                ("c2", "Colonne 2", 160),
                ("c3", "Colonne 3", 120),
                ("c4", "Colonne 4", 120),
                ("c5", "Colonne 5", 120),
                ("c6", "Colonne 6", 120),
            ],
            empty_title="Aucun rapport",
            empty_message="Choisissez un type et cliquez sur Générer.",
        )
        self.table.pack(fill="both", expand=True, padx=28, pady=(0, 24))

    def _generate(self) -> None:
        kind = self.report_type.get()
        cat_map = {c.id: c.name for c in self.ctx.categories.get_all()}

        if kind == "Rapport stock":
            products = self.ctx.products.get_all()
            headers = ["Code", "Produit", "Catégorie", "Stock", "P.Achat", "Valeur"]
            rows = [
                [
                    p.code, p.name, cat_map.get(p.category_id, "—"),
                    p.quantity, f"{p.purchase_price:.3f}", f"{p.stock_value:.3f}",
                ]
                for p in products
            ]
            total_value = sum(p.stock_value for p in products)
            self.summary.configure(
                text=f"{len(products)} produits — Valeur stock : {format_tnd(total_value)}"
            )
        elif kind == "Stock faible / ruptures":
            products = self.ctx.products.get_out_of_stock() + self.ctx.products.get_low_stock()
            headers = ["Code", "Produit", "Stock", "Min", "État", ""]
            rows = [
                [
                    p.code, p.name, p.quantity, p.min_stock,
                    "Rupture" if p.is_out_of_stock else "Faible", "",
                ]
                for p in products
            ]
            self.summary.configure(text=f"{len(products)} alerte(s)")
        elif kind.startswith("Ventes"):
            if "jour" in kind:
                sales = self.ctx.sales.get_today()
            elif "semaine" in kind:
                sales = self.ctx.sales.get_week()
            else:
                sales = self.ctx.sales.get_month()
            headers = ["N°", "Date", "Client", "Vendeur", "Total", "Paiement"]
            rows = [
                [s.id, s.date, s.customer_name, s.username, f"{s.total:.3f}", s.payment_method]
                for s in sales
            ]
            self.summary.configure(
                text=f"{len(sales)} vente(s) — Total : {format_tnd(sum(s.total for s in sales))}"
            )
        elif kind == "Achats par fournisseur":
            purchases = self.ctx.purchases.get_all()
            by_sup: dict[str, float] = {}
            for p in purchases:
                by_sup[p.supplier_name] = by_sup.get(p.supplier_name, 0) + p.total
            headers = ["Fournisseur", "Total achats (TND)", "", "", "", ""]
            rows = [[name, f"{total:.3f}", "", "", "", ""] for name, total in by_sup.items()]
            self.summary.configure(text=f"{len(by_sup)} fournisseur(s)")
        else:
            purchases = (
                self.ctx.purchases.get_today()
                if "jour" in kind
                else self.ctx.purchases.get_month()
            )
            headers = ["N°", "Date", "Fournisseur", "Utilisateur", "Total", ""]
            rows = [
                [p.id, p.date, p.supplier_name, p.username, f"{p.total:.3f}", ""]
                for p in purchases
            ]
            self.summary.configure(
                text=f"{len(purchases)} achat(s) — Total : {format_tnd(sum(p.total for p in purchases))}"
            )

        self.current_title = kind
        self.current_headers = headers
        self.current_rows = rows
        display_rows = [r[:6] for r in rows]
        self.table.set_rows(display_rows)

    def _export(self, fmt: str) -> None:
        if not self.current_rows:
            self._generate()
        if not self.current_rows and not self.current_headers:
            show_error("Rapports", "Aucune donnée à exporter.")
            return

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe = self.current_title.replace(" ", "_").replace("/", "-")
        if fmt == "csv":
            path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                initialfile=f"{safe}_{stamp}.csv",
                initialdir=str(self.ctx.reports_dir),
            )
            if path:
                export_csv(path, self.current_headers, self.current_rows)
                show_info("Export", f"CSV enregistré :\n{path}")
                toast(self, "CSV exporté", "success")
        elif fmt == "excel":
            path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=f"{safe}_{stamp}.xlsx",
                initialdir=str(self.ctx.reports_dir),
            )
            if path:
                try:
                    export_excel(path, self.current_headers, self.current_rows, self.current_title)
                    show_info("Export", f"Excel enregistré :\n{path}")
                    toast(self, "Excel exporté", "success")
                except Exception as exc:
                    show_error("Export", str(exc))
        else:
            path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                initialfile=f"{safe}_{stamp}.pdf",
                initialdir=str(self.ctx.reports_dir),
            )
            if path:
                try:
                    export_pdf(
                        path, self.current_title,
                        self.current_headers, self.current_rows,
                        subtitle="StockTN Desktop — Dinars Tunisiens (TND)",
                    )
                    show_info("Export", f"PDF enregistré :\n{path}")
                    toast(self, "PDF exporté", "success")
                except Exception as exc:
                    show_error("Export", str(exc))
