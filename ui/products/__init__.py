from __future__ import annotations

import customtkinter as ctk
from tkinter import simpledialog

from models.user import User
from services.app_context import AppContext
from ui import COLORS, FONT_FAMILY, RADIUS
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
    show_info,
    style_dialog,
    styled_combo,
    styled_entry,
    toast,
)
from utils.images import list_product_images, load_ctk_image
from utils.validators import format_tnd

class ProductsView(ctk.CTkFrame):
    def __init__(self, master, ctx: AppContext, user: User):
        super().__init__(master, fg_color=COLORS["bg"])
        self.ctx = ctx
        self.user = user
        self.can_edit = user.role == "admin"
        self._preview_img = None
        self._build()
        self.refresh()

    def _build(self) -> None:
        title = "Produits" if self.can_edit else "Catalogue produits"
        PageHeader(
            self, title, "Recherche par code, nom, code-barres, marque", icon="products"
        ).pack(fill="x", padx=28, pady=(22, 14))

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=28, pady=(0, 10))

        self.search = styled_entry(toolbar, placeholder_text="Rechercher…", width=220)
        self.search.pack(side="left", padx=(0, 8))
        self.search.bind("<KeyRelease>", lambda e: self.refresh())

        cats = ["Toutes"] + [c.name for c in self.ctx.categories.get_all(active_only=True)]
        self.cat_filter = styled_combo(toolbar, values=cats, width=160)
        self.cat_filter.set("Toutes")
        self.cat_filter.pack(side="left", padx=(0, 8))
        self.cat_filter.configure(command=lambda _: self.refresh())

        self.stock_filter = styled_combo(
            toolbar,
            values=["Tous", "Disponibles", "Stock faible", "Rupture"],
            width=140,
            command=lambda _: self.refresh(),
        )
        self.stock_filter.set("Tous")
        self.stock_filter.pack(side="left", padx=(0, 8))

        GhostButton(
            toolbar, text=" Actualiser", icon="refresh-cw", width=120, command=self.refresh
        ).pack(side="left")

        if self.can_edit:
            SuccessButton(toolbar, text=" Ajouter", width=120, command=self._add).pack(
                side="right", padx=(8, 0)
            )
            SecondaryButton(
                toolbar, text=" Modifier", icon="pencil", width=120, command=self._edit
            ).pack(side="right", padx=(8, 0))
            DangerButton(toolbar, text=" Supprimer", width=120, command=self._delete).pack(
                side="right"
            )
        elif self.user.role == "client":
            PrimaryButton(
                toolbar, text=" Commander", icon="shopping-bag", width=130, command=self._order_product
            ).pack(side="right")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=28, pady=(0, 24))

        cols = [
            ("code", "Code", 90),
            ("barcode", "Code-barres", 110),
            ("name", "Désignation", 180),
            ("category", "Catégorie", 100),
            ("brand", "Marque", 90),
            ("price", "Prix vente", 100),
            ("qty", "Stock", 70),
            ("status", "État", 90),
        ]
        if self.can_edit:
            cols.insert(5, ("buy", "Prix achat", 100))

        self.table = DataTable(
            body,
            cols,
            on_select=lambda _: self._show_preview(),
            empty_title="Aucun produit",
            empty_message="Ajoutez un produit ou modifiez vos filtres.",
        )
        self.table.pack(side="left", fill="both", expand=True, padx=(0, 12))

        preview = ctk.CTkFrame(
            body,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["md"],
            width=250,
            border_width=1,
            border_color=COLORS["border"],
        )
        preview.pack(side="right", fill="y")
        preview.pack_propagate(False)
        ctk.CTkLabel(
            preview,
            text="Aperçu",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color=COLORS["text"],
        ).pack(pady=(18, 8))
        self.preview_label = ctk.CTkLabel(
            preview,
            text="Sélectionnez\nun produit",
            text_color=COLORS["text_muted"],
            width=200,
            height=200,
            fg_color=COLORS["surface_hover"],
            corner_radius=RADIUS["sm"],
        )
        self.preview_label.pack(padx=16, pady=8)
        self.preview_name = ctk.CTkLabel(
            preview,
            text="",
            wraplength=200,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLORS["text"],
        )
        self.preview_name.pack(padx=12, pady=(4, 4))
        self.preview_price = ctk.CTkLabel(
            preview,
            text="",
            text_color=COLORS["primary"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
        )
        self.preview_price.pack(padx=12, pady=(0, 16))

    def _show_preview(self) -> None:
        pid = self._selected_id()
        if not pid:
            return
        product = self.ctx.products.get_by_id(pid)
        if not product:
            return
        img = load_ctk_image(product.image, (200, 200))
        self._preview_img = img
        if img:
            self.preview_label.configure(image=img, text="")
        else:
            self.preview_label.configure(image=None, text="Pas d'image")
        self.preview_name.configure(text=product.name)
        self.preview_price.configure(text=format_tnd(product.sale_price))

    def _category_map(self) -> dict:
        return {c.id: c.name for c in self.ctx.categories.get_all()}

    def _availability_key(self) -> str:
        mapping = {
            "Tous": "all",
            "Disponibles": "available",
            "Stock faible": "low",
            "Rupture": "out",
        }
        return mapping.get(self.stock_filter.get(), "all")

    def _selected_category_id(self):
        name = self.cat_filter.get()
        if name == "Toutes":
            return None
        for c in self.ctx.categories.get_all():
            if c.name == name:
                return c.id
        return None

    def refresh(self) -> None:
        cat_map = self._category_map()
        products = self.ctx.products.search(
            query=self.search.get(),
            category_id=self._selected_category_id(),
            availability=self._availability_key(),
        )
        rows, iids = [], []
        for p in products:
            status = (
                "Rupture" if p.is_out_of_stock
                else "Stock faible" if p.is_low_stock
                else "OK"
            )
            cat = cat_map.get(p.category_id, "—")
            if self.can_edit:
                row = (
                    p.code, p.barcode, p.name, cat, p.brand,
                    format_tnd(p.purchase_price), format_tnd(p.sale_price),
                    p.quantity, status,
                )
            else:
                row = (
                    p.code, p.barcode, p.name, cat, p.brand,
                    format_tnd(p.sale_price), p.quantity, status,
                )
            rows.append(row)
            iids.append(p.id)
        self.table.set_rows(rows, iids)

    def _selected_id(self):
        iid = self.table.get_selected()
        return int(iid) if iid else None

    def _dialog(self, product=None) -> None:
        dialog = ProductFormDialog(self, self.ctx, product)
        self.wait_window(dialog)
        if dialog.result:
            self.refresh()
            toast(self, "Produit enregistré", "success")

    def _add(self) -> None:
        self._dialog()

    def _edit(self) -> None:
        pid = self._selected_id()
        if not pid:
            show_error("Produits", "Sélectionnez un produit.")
            return
        product = self.ctx.products.get_by_id(pid)
        self._dialog(product)

    def _delete(self) -> None:
        pid = self._selected_id()
        if not pid:
            show_error("Produits", "Sélectionnez un produit.")
            return
        if ask_confirm("Supprimer", "Supprimer ce produit ?"):
            try:
                self.ctx.products.delete(pid)
                self.refresh()
                toast(self, "Produit supprimé", "success")
            except ValueError as exc:
                show_error("Produits", str(exc))

    def _order_product(self) -> None:
        pid = self._selected_id()
        if not pid:
            show_error("Catalogue", "Sélectionnez un produit.")
            return
        if not self.user.customer_id:
            show_error("Commande", "Aucun profil client associé.")
            return
        product = self.ctx.products.get_by_id(pid)
        if not product or product.quantity <= 0:
            show_error("Commande", "Produit indisponible.")
            return
        qty = simpledialog.askinteger(
            "Quantité", f"Quantité pour {product.name} :",
            minvalue=1, maxvalue=product.quantity, parent=self,
        )
        if not qty:
            return
        try:
            self.ctx.orders.create_order(
                self.user.customer_id,
                [{"product_id": product.id, "quantity": qty}],
            )
            show_info("Commande", "Commande créée avec le statut « En attente ».")
            toast(self, "Commande créée", "success")
        except ValueError as exc:
            show_error("Commande", str(exc))

class ProductFormDialog(ctk.CTkToplevel):
    def __init__(self, master, ctx: AppContext, product=None):
        super().__init__(master)
        self.ctx = ctx
        self.product = product
        self.result = False
        self._preview_img = None
        style_dialog(self, "Produit" if product else "Nouveau produit", "520x720")
        self.resizable(False, False)
        self._build()

    def _build(self) -> None:
        frame = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg"])
        frame.pack(fill="both", expand=True, padx=16, pady=16)
        p = self.product
        cats = self.ctx.categories.get_all(active_only=True)
        cat_names = [c.name for c in cats] or ["—"]
        self._cats = {c.name: c.id for c in cats}

        fields = [
            ("code", "Code produit", p.code if p else ""),
            ("barcode", "Code-barres", p.barcode if p else ""),
            ("name", "Désignation", p.name if p else ""),
            ("brand", "Marque", p.brand if p else ""),
            ("purchase_price", "Prix d'achat (TND)", str(p.purchase_price if p else "")),
            ("sale_price", "Prix de vente (TND)", str(p.sale_price if p else "")),
            ("quantity", "Quantité", str(p.quantity if p else "0")),
            ("min_stock", "Stock minimum", str(p.min_stock if p else "0")),
            ("unit", "Unité", p.unit if p else "unité"),
            ("description", "Description", p.description if p else ""),
        ]
        self.entries = {}
        for key, label, value in fields:
            ctk.CTkLabel(
                frame, text=label, anchor="w", text_color=COLORS["text_muted"],
                font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            ).pack(fill="x", pady=(8, 0))
            entry = styled_entry(frame)
            entry.insert(0, value)
            entry.pack(fill="x", pady=(4, 0))
            self.entries[key] = entry

        ctk.CTkLabel(
            frame, text="Catégorie", anchor="w", text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        ).pack(fill="x", pady=(8, 0))
        self.cat_box = styled_combo(frame, values=cat_names)
        if p:
            for name, cid in self._cats.items():
                if cid == p.category_id:
                    self.cat_box.set(name)
                    break
            else:
                self.cat_box.set(cat_names[0])
        else:
            self.cat_box.set(cat_names[0])
        self.cat_box.pack(fill="x", pady=(4, 0))

        images = ["(aucune)"] + list_product_images()
        ctk.CTkLabel(
            frame, text="Image produit", anchor="w", text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        ).pack(fill="x", pady=(8, 0))
        self.image_box = styled_combo(
            frame, values=images, command=self._update_image_preview
        )
        current = p.image if p and p.image else "(aucune)"
        if current not in images:
            images.append(current)
            self.image_box.configure(values=images)
        self.image_box.set(current)
        self.image_box.pack(fill="x", pady=(4, 0))

        self.img_preview = ctk.CTkLabel(
            frame, text="", width=140, height=140,
            fg_color=COLORS["surface"], corner_radius=RADIUS["sm"],
        )
        self.img_preview.pack(pady=12)
        self._update_image_preview(self.image_box.get())

        btns = ctk.CTkFrame(frame, fg_color="transparent")
        btns.pack(fill="x", pady=16)
        PrimaryButton(btns, text=" Enregistrer", icon="check", command=self._save).pack(
            side="right"
        )
        GhostButton(btns, text="Annuler", command=self.destroy).pack(side="right", padx=8)

    def _update_image_preview(self, value: str) -> None:
        name = value if value != "(aucune)" else ""
        img = load_ctk_image(name, (140, 140)) if name else None
        self._preview_img = img
        if img:
            self.img_preview.configure(image=img, text="")
        else:
            self.img_preview.configure(image=None, text="Pas d'image")

    def _save(self) -> None:
        try:
            data = {k: e.get() for k, e in self.entries.items()}
            data["category_id"] = self._cats.get(self.cat_box.get(), 0)
            img = self.image_box.get()
            data["image"] = "" if img == "(aucune)" else img
            if self.product:
                self.ctx.products.update(self.product.id, **data)
            else:
                self.ctx.products.create(**data)
            self.result = True
            self.destroy()
        except ValueError as exc:
            show_error("Produit", str(exc))
