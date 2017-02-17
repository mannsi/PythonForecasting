import math
import logging
from typing import List, Dict
from forecast.data_structures.records import ItemDateQuantityRecord


def drop_first_and_last_values_for_each_item(grouped_forecast_records):
    updated_dict = {}
    for item_id, item_records in grouped_forecast_records.items():
        all_dates_for_item = [x.date for x in item_records]
        item_records = [x for x in item_records if x.date != max(all_dates_for_item)]
        item_records = [x for x in item_records if x.date != min(all_dates_for_item)]
        updated_dict[item_id] = item_records

    return updated_dict


def remove_nan_quantity_values(item_date_quantity_list: Dict[str,List[ItemDateQuantityRecord]]):
    """
    Takes a Dict[item_id, List[ItemDateQuantityRecord]] and returns the same data structure where only items with numeric quantities are kept
    """
    cleaned_dict = {}

    for item_id, item_records in item_date_quantity_list.items():
        cleaned_list = [x for x in item_records if not math.isnan(x.quantity)]
        cleaned_dict[item_id] = cleaned_list

    return cleaned_dict


def remove_items_with_no_predictions(sales_records:Dict[str,List[ItemDateQuantityRecord]], forecast_records:Dict[str,List[ItemDateQuantityRecord]]):
    cleaned_item_sales_dict = {}
    cleaned_item_prediction_dict = {}

    for sales_item_id, item_sales_records in sales_records.items():
        if sales_item_id not in forecast_records:
            logging.WARNING("No prediction values found for item with id {0]".format(sales_item_id))
            continue

        predicted_records_for_item = forecast_records[sales_item_id]
        number_of_predictions_for_item = len([x for x in predicted_records_for_item if x.quantity is not None])
        if number_of_predictions_for_item == 0:
            logging.WARNING("No prediction values found for item with id {0]".format(sales_item_id))
            continue

        cleaned_item_sales_dict[sales_item_id] = item_sales_records
        cleaned_item_prediction_dict[sales_item_id] = predicted_records_for_item

    return cleaned_item_sales_dict, cleaned_item_prediction_dict