import pandas as pd


def by_week_sums(dates, values):
    df = pd.DataFrame(index=dates)
    df["qty"] = values
    grouped_data = df.qty.resample('W').sum()
    return grouped_data.index, grouped_data


def by_month_sums(dates, values):
    df = pd.DataFrame(index=dates)
    df["qty"] = values
    grouped_data = df.qty.resample('M').sum()
    return grouped_data.index, grouped_data
