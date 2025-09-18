# FILE: inventory_manager.py
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