import pandas as pd
import math
import logging
from forecast.data_structures.records import SaleAndPredictionRecord


def group_by_dates(dates, qty, period):
    df = pd.DataFrame(index=dates)
    df["qty"] = qty
    grouped_qty = df.qty.resample(period).sum()
    return grouped_qty.index, grouped_qty


def join_dicts(sales_record_dict, prediction_record_dict):
    """
    :param sales_record_dict:  {item_id: list of ItemDateQuantityRecord}
    :param prediction_record_dict: {item_id: list of ItemDateQuantityRecord}
    :return dict{item_id: List[SaleAndPredictionRecord]}
    """
    all_items_sales_and_predictions = {}

    for item_id, sale_records_for_item in sales_record_dict.items():
        sale_and_predictions_list = []
        predicted_records_for_item = prediction_record_dict[item_id]

        for sale_record in sale_records_for_item:
            predicted_qty = None
            for predicted_record in predicted_records_for_item:
                if predicted_record.date == sale_record.date:
                    predicted_qty = predicted_record.quantity
                    break
            sale_and_predictions_list.append(
                SaleAndPredictionRecord(sale_record.item_id, sale_record.date, sale_record.quantity, predicted_qty))

        all_items_sales_and_predictions[item_id] = sale_and_predictions_list
    return all_items_sales_and_predictions

