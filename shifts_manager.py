# FILE: shifts_manager.py
"""
Shifts manager: stores shift records and computes simple compliance metrics.
"""
import pandas as pd
from datetime import datetime


class ShiftsManager:
def __init__(self):
self._shifts = []


def add_shift(self, worker_name, clock_in_iso, clock_out_iso, cleaning, orderly, petty):
rec = {
'id': len(self._shifts) + 1,
'worker': worker_name,
'clock_in': clock_in_iso,
'clock_out': clock_out_iso,
'cleaning': 1 if cleaning else 0,
'orderly': 1 if orderly else 0,
'restock': 1 if petty else 0,
}
self._shifts.append(rec)
return True


def df(self):
if not self._shifts:
return pd.DataFrame(columns=['id','worker','clock_in','clock_out','cleaning','orderly','restock'])
return pd.DataFrame(self._shifts)


def overall_compliance_rate(self):
df = self.df()
if df.empty:
return 0.0
# three checks per shift: average of all checks, expressed in percent
df['mean'] = df[['cleaning','orderly','restock']].mean(axis=1)
return 100.0 * df['mean'].mean()


def compliance_summary(self):
df = self.df()
if df.empty:
return {'cleaning_avg': None, 'orderly_avg': None, 'restock_avg': None, 'records':0}
return {
'cleaning_avg': df['cleaning'].mean(),
'orderly_avg': df['orderly'].mean(),
'restock_avg': df['restock'].mean(),
'records': len(df)
}


# EOF