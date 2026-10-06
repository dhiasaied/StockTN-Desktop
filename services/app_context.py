from __future__ import annotations

from pathlib import Path

from services.auth_service import AuthService
from services.category_service import CategoryService
from services.customer_service import CustomerService
from services.order_service import OrderService
from services.product_service import ProductService
from services.purchase_service import PurchaseService
from services.sale_service import SaleService
from services.stock_service import StockService
from services.supplier_service import SupplierService
from utils.backup import BackupManager
from utils.json_storage import JsonStorage

class AppContext:

    def __init__(self, root_dir: Path) -> None:
        self.root_dir = Path(root_dir)
        self.data_dir = self.root_dir / "data"
        self.backups_dir = self.root_dir / "backups"
        self.reports_dir = self.root_dir / "reports"
        self.assets_dir = self.root_dir / "assets"

        for d in (self.data_dir, self.backups_dir, self.reports_dir, self.assets_dir):
            d.mkdir(parents=True, exist_ok=True)

        self.storage = JsonStorage(self.data_dir)
        self.backup = BackupManager(self.data_dir, self.backups_dir)

        self.auth = AuthService(self.storage)
        self.categories = CategoryService(self.storage)
        self.products = ProductService(self.storage)
        self.customers = CustomerService(self.storage)
        self.suppliers = SupplierService(self.storage)
        self.stock = StockService(self.storage, self.products)
        self.sales = SaleService(self.storage, self.products, self.stock)
        self.purchases = PurchaseService(
            self.storage, self.products, self.stock, self.suppliers
        )
        self.orders = OrderService(self.storage, self.products, self.customers)

        self.current_user = None
