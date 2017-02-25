import csv
import datetime
from typing import Dict, List
from forecast.data_structures.records import ItemDateQuantityRecord


def get_sample_forecast_values(file_path) -> Dict[str, List[ItemDateQuantityRecord]]:
    """
    :return: dict of {item_id: list of ItemDateQuantityRecord}
    """
    with open(file_path) as f:
        next(f)  # skip heading
        next(f)  # skip heading
        data_records = {}
        reader = csv.reader(f, delimiter='\t')
        for item_id, random_value, date_string, qty_string in reader:
            record = ItemDateQuantityRecord(item_id, datetime.datetime.strptime(date_string, "%Y-%m-%d"), float(qty_string))
            if record.item_id not in data_records:
                data_records[record.item_id] = []
            data_records[record.item_id].append(record)
    return data_records


def get_sample_history_sales_values(file_path):
    """
    :return: dict of {item_id: list of ItemDateQuantityRecord}
    """
    with open(file_path) as f:
        next(f)  # skip headings
        data_records = {}
        reader = csv.reader(f, delimiter='\t')
        for item_id, date_string, qty_string in reader:
            record = ItemDateQuantityRecord(item_id, datetime.datetime.strptime(date_string, "%Y-%m-%d"), float(qty_string))
            if record.item_id not in data_records:
                data_records[record.item_id] = []
            data_records[record.item_id].append(record)
    return data_records
