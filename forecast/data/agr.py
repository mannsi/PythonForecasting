import logging
import os
import pickle
from typing import Tuple, List, Dict

import forecast.IO.file_reader as file_reader
import forecast.data.clean as clean
import forecast.data.group as group
from forecast.data.structures import ItemDateQuantityRecord


def get_data(period, date_shift):
    # Get the data from files and clean it
    sales_records, forecast_pro_forecast_records = _get_forecast_and_sales_records(period, date_shift)
    logging.debug("Sales records: {0}, forecast records: {1}"
                  .format(len(sales_records), len(forecast_pro_forecast_records)))
    sales_records, forecast_pro_forecast_records = clean.remove_items_with_no_predictions(sales_records,
                                                                                          forecast_pro_forecast_records)
    logging.debug("Sales records: {0}, forecast records: {1} after cleaning"
                  .format(len(sales_records), len(forecast_pro_forecast_records)))

    return sales_records, forecast_pro_forecast_records


def _get_forecast_and_sales_records(
        group_by: str,
        days_to_shift: int) -> Tuple[Dict[str, List[ItemDateQuantityRecord]], Dict[str, List[ItemDateQuantityRecord]]]:
    """
    Gets the tuple grouped_sales_records, grouped_forecast_records
    :param days_to_shift:
    :param group_by: 'W' or 'M'
    :return: ({item_id: list of sales records}, {item_id: list of forecast records})
    """
    files_directory = os.path.join("data", "files")
    forecast_value_pickle_file = os.path.join(files_directory, group_by + "forecast_values.pickle")
    sales_values_pickle_file = os.path.join(files_directory, group_by + "sales_values.pickle")

    try:
        grouped_forecast_records = pickle.load(open(forecast_value_pickle_file, "rb"))
        logging.debug("Loading forecast list from memory")
    except (OSError, IOError) as e:
        forecast_file_abs_path = os.path.abspath(os.path.join(files_directory, "forecast_values.txt"))
        forecast_records = file_reader.get_sample_forecast_values(forecast_file_abs_path)

        # Shift the data so it fits nicely f.x. to weeks or months
        for item_id, records_for_item in forecast_records.items():
            clean.shift_data_by_days(records_for_item, days_to_shift)

        grouped_forecast_records = _group_item_quantity_records(forecast_records, group_by)
        grouped_forecast_records = clean.remove_nan_quantity_values(grouped_forecast_records)
        pickle.dump(grouped_forecast_records, open(forecast_value_pickle_file, "wb"))

        num_forecast_records = sum([len(item_records) for item_id, item_records in forecast_records.items()])
        logging.info("Found {0} items with {1} number of forecast values and grouped them down to {2}"
                     .format(len(forecast_records), num_forecast_records, len(grouped_forecast_records)))

    try:
        grouped_sales_records = pickle.load(open(sales_values_pickle_file, "rb"))
        logging.debug("Loading sales list from memory")
    except (OSError, IOError) as e:
        sales_file_abs_path = os.path.abspath(os.path.join(files_directory, "histories_sales.txt"))
        sales_records = file_reader.get_sample_history_sales_values(sales_file_abs_path)

        # Shift the data so it fits nicely f.x. to weeks or months
        for item_id, records_for_item in sales_records.items():
            clean.shift_data_by_days(records_for_item, days_to_shift)

        grouped_sales_records = _group_item_quantity_records(sales_records, group_by)
        grouped_sales_records = clean.remove_nan_quantity_values(grouped_sales_records)

        # First record is not a whole month. That is why we remove it
        grouped_sales_records = clean.drop_first_values_for_each_item(grouped_sales_records)
        pickle.dump(grouped_sales_records, open(sales_values_pickle_file, "wb"))
        num_sales_records = sum([len(item_records) for item_id, item_records in sales_records.items()])
        logging.info("Found {0} items with {1} number of sales values and grouped them down to {2}"
                     .format(len(sales_records), num_sales_records, len(grouped_sales_records)))

    return grouped_sales_records, grouped_forecast_records


def _group_item_quantity_records(
        item_quantity_records: Dict[str, List[ItemDateQuantityRecord]],
        group_by: str) -> Dict[str, List[ItemDateQuantityRecord]]:
    """

    :param initial_date: The initial date that should be grouped from
    :param item_quantity_records: {item_id: list of ItemDateQuantityRecord}
    :param group_by: Either 'W' or 'M" for weeks and months
    :return: {item_id: list of ItemDateQuantityRecord}
    """
    grouped_item_quantity_dict = {}
    for item_id, item_records in item_quantity_records.items():
        grouped_item_quantity_dict[item_id] = []
        dates = [x.date for x in item_records]
        quantities = [x.quantity for x in item_records]
        grouped_dates, grouped_quantities = group.group_by_dates(dates, quantities, group_by)
        for i in range(len(grouped_dates)):
            date = grouped_dates[i]
            quantity = grouped_quantities[i]
            grouped_record = ItemDateQuantityRecord(item_id, date, quantity)
            grouped_item_quantity_dict[item_id].append(grouped_record)

    return grouped_item_quantity_dict
