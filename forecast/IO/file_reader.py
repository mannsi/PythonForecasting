import csv
import datetime


def get_sample_forecast_values(file_path):
    """
    :return: list of tuples [item_id, date_string, predicted_qty_decimal]
    """
    with open(file_path) as f:
        # lines = f.readlines()
        next(f)  # skip headings
        next(f)  # skip headings
        data_rows = []
        reader = csv.reader(f, delimiter='\t')
        for item_id, random_value, date_string, qty_string in reader:
            data_rows.append((item_id, datetime.datetime.strptime(date_string, "%Y-%m-%d"), float(qty_string)))
    return data_rows

def get_sample_history_sales_values(file_path):
    """
    :return: list of tuples [item_id, date_string, sold_qty_decimal]
    """
    with open(file_path) as f:
        # lines = f.readlines()
        next(f)  # skip headings
        data_rows = []
        reader = csv.reader(f, delimiter='\t')
        for item_id, date_string, qty_string in reader:
            data_rows.append((item_id, datetime.datetime.strptime(date_string, "%Y-%m-%d"), float(qty_string)))
    return data_rows
