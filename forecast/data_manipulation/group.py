import pandas as pd


def group_by_dates(dates, qty, period):
    df = pd.DataFrame(index=dates)
    df["qty"] = qty
    grouped_qty = df.qty.resample(period).sum()
    return grouped_qty.index, grouped_qty


