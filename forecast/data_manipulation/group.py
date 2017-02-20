import pandas as pd
import math
import logging
from typing import List, Dict
from forecast.data_structures.records import SaleAndPredictionRecord,ItemDateQuantityRecord


def group_by_dates(dates, qty, period):
    df = pd.DataFrame(index=dates)
    df["qty"] = qty
    grouped_qty = df.qty.resample(period).sum()
    return grouped_qty.index, grouped_qty


def join_sales_and_predictions(sales_record_dict: Dict[str, List[ItemDateQuantityRecord]],
                               prediction_record_dict: Dict[str, List[ItemDateQuantityRecord]],
                               only_predicted_dates: bool) -> Dict[str, List[SaleAndPredictionRecord]]:
    """
    :param sales_record_dict:
    :param prediction_record_dict: {item_id: list of ItemDateQuantityRecord}
    :param only_predicted_dates: if the output should only include dates with predicted values or all sales dates
    :return dict{item_id: List[SaleAndPredictionRecord]}
    """
    all_items_sales_and_predictions = {}

    for item_id, sale_records_for_item in sales_record_dict.items():
        predicted_records_for_item = prediction_record_dict[item_id]
        joined_lists = zip_item_lists_on_date(sale_records_for_item, predicted_records_for_item, only_predicted_dates)
        all_items_sales_and_predictions[item_id] = joined_lists
    return all_items_sales_and_predictions


def zip_item_lists_on_date(sales_records: List[ItemDateQuantityRecord],
                           prediction_records: List[ItemDateQuantityRecord],
                           only_predicted_dates: bool)-> List[SaleAndPredictionRecord]:
    output_list = []

    for sale_record in sales_records:
        predicted_qty = None

        for predicted_record in prediction_records:
            if predicted_record.date == sale_record.date:
                predicted_qty = predicted_record.quantity
                if only_predicted_dates:
                    output_list.append(
                        SaleAndPredictionRecord(sale_record.item_id, sale_record.date, sale_record.quantity,
                                                predicted_qty))
                break
        if not only_predicted_dates:
            output_list.append(SaleAndPredictionRecord(sale_record.item_id, sale_record.date, sale_record.quantity, predicted_qty))

    return output_list
