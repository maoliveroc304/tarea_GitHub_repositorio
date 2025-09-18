# FILE: inventory_manager.py
"""
Inventory manager: simple in-memory CRUD for products.
Uses session-safe lists/dicts.
"""
import pandas as pd
import uuid

class InventoryManager:
    def __init__(self):
        # initialize with empty list or existing session data
        self._products = []

    def df(self):
        if not self._products:
            return pd.DataFrame(columns=['product_id','product_name','sku','category','stock','reorder_level','price'])
        return pd.DataFrame(self._products)

    def add_product(self, name, sku, category, stock, reorder_level, price):
        pid = str(uuid.uuid4())
        item = {
            'product_id': pid,
            'product_name': name,
            'sku': sku,
            'category': category,
            'stock': int(stock),
            'reorder_level': int(reorder_level) if reorder_level is not None else 0,
            'price': float(price) if price is not None else 0.0
        }
        self._products.append(item)
        return pid

    def get_by_id(self, pid):
        for p in self._products:
            if p['product_id'] == pid:
                return p
        return None

    def edit_product(self, pid, name, sku, category, stock, reorder_level, price):
        p = self.get_by_id(pid)
        if not p:
            return False
        p['product_name'] = name
        p['sku'] = sku
        p['category'] = category
        p['stock'] = int(stock)
        p['reorder_level'] = int(reorder_level)
        p['price'] = float(price)
        return True

    def delete_product(self, pid):
        self._products = [p for p in self._products if p['product_id'] != pid]
        return True

    def update_stock(self, pid, delta):
        p = self.get_by_id(pid)
        if not p:
            return False
        new_stock = int(p['stock']) + int(delta)
        if new_stock < 0:
            new_stock = 0
        p['stock'] = new_stock
        return True

    # KPI helpers
    def total_skus(self):
        return len(self._products)

    def total_units(self):
        return sum(int(p['stock']) for p in self._products)

    def average_stock(self):
        if not self._products:
            return 0.0
        return float(self.total_units()) / max(1, self.total_skus())

    def low_stock_percentage(self):
        if not self._products:
            return 0.0
        low = 0
        for p in self._products:
            if p.get('reorder_level',0) is None:
                continue
            if int(p['stock']) <= int(p.get('reorder_level',0)):
                low += 1
        return 100.0 * low / self.total_skus()
