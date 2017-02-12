import pandas as pd
from datetime import datetime, timedelta



listi = [[datetime.now() + timedelta(days=1), 10],
         [datetime.now() + timedelta(days=2), 50],
         [datetime.now() + timedelta(days=2), 101],
         [datetime.now() + timedelta(days=8), None]]

dates = [x[0] for x in listi]
values = [x[1] for x in listi]

df = pd.DataFrame(index = dates)

df["qty"] = values

dfhead = df.head()
# print(dfhead)

bla = df.qty.resample('W').sum()
print(bla.index)
print(list(bla))

weekly_summary = pd.DataFrame()
weekly_summary['weekly_qty_sum'] = df.qty.resample('W').sum()

# print(weekly_summary.head())