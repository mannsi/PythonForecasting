import logging
import os
import pickle
from typing import List

import forecast.IO.file_reader as file_reader
import forecast.data_structures.records as records
import forecast.graphs.quantitygraph as quantity_graph
import forecast.data_manipulation.group as group
from forecast.models.agr.mock_model import MockModel
from forecast.models.machine_learning.neural_network import NeuralNetwork
from forecast.data_structures.records import ItemDateQuantityRecord

def init_logging():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def drop_first_and_last_values_for_each_item(grouped_forecast_records):
    updated_dict = {}
    for item_id, item_records in grouped_forecast_records.items():
        all_dates_for_item = [x.date for x in item_records]
        item_records = [x for x in item_records if x.date != max(all_dates_for_item)]
        item_records = [x for x in item_records if x.date != min(all_dates_for_item)]
        updated_dict[item_id] = item_records

    return updated_dict


def get_forecast_and_sales_records(group_by):
    """
    Gets the tuple grouped_sales_records, grouped_forecast_records
    :param group_by: string
    :return: ({item_id: list of records.ItemDateQuantityRecord}, {item_id: list of records..ItemDateQuantityRecord})
    """
    forecast_value_pickle_file = group_by + "forecast_values.pickle"
    sales_values_pickle_file = group_by + "sales_values.pickle"

    try:
        grouped_forecast_records = pickle.load(open(forecast_value_pickle_file, "rb"))
        logging.debug("Loading forecast list from memory")
    except (OSError, IOError) as e:
        forecast_file_abs_path = os.path.abspath(os.path.join("files", "forecast_values.txt"))
        forecast_records = file_reader.get_sample_forecast_values(forecast_file_abs_path)
        grouped_forecast_records = group_item_quantity_records(forecast_records, group_by)
        grouped_forecast_records = drop_first_and_last_values_for_each_item(grouped_forecast_records)
        pickle.dump(grouped_forecast_records, open(forecast_value_pickle_file, "wb"))

        num_forecast_records = sum([len(item_records) for item_id, item_records in forecast_records.items()])
        logging.debug("Found {0} items with {1} number of forecast values and grouped them down to {2}"
                      .format(len(forecast_records), num_forecast_records, len(grouped_forecast_records)))

    try:
        grouped_sales_records = pickle.load(open(sales_values_pickle_file, "rb"))
        logging.debug("Loading sales list from memory")
    except (OSError, IOError) as e:
        sales_file_abs_path = os.path.abspath(os.path.join("files", "histories_sales.txt"))
        sales_records = file_reader.get_sample_history_sales_values(sales_file_abs_path)
        grouped_sales_records = group_item_quantity_records(sales_records, group_by)
        grouped_sales_records = drop_first_and_last_values_for_each_item(grouped_sales_records)
        pickle.dump(grouped_sales_records, open(sales_values_pickle_file, "wb"))

        num_sales_records = sum([len(item_records) for item_id, item_records in sales_records.items()])
        logging.debug("Found {0} items with {1} number of sales values and grouped them down to {2}"
                      .format(len(sales_records), num_sales_records,len(grouped_sales_records)))

    return grouped_sales_records, grouped_forecast_records


def group_item_quantity_records(item_quantity_records, group_by):
    """

    :param item_quantity_records: {item_id: list of records.ItemDateQuantityRecord}
    :param group_by: string
    :return: {item_id: list of records.ItemDateQuantityRecord}
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
            grouped_record = records.ItemDateQuantityRecord(item_id, date, quantity)
            grouped_item_quantity_dict[item_id].append(grouped_record)

    return grouped_item_quantity_dict


def join_sales_and_forecasts(sales_records: List[ItemDateQuantityRecord], forecast_records: List[ItemDateQuantityRecord], period):
    sale_and_predictions_pickle_file = period + "sale_and_predictions_list.pickle"
    try:
        sale_and_predictions_dict = pickle.load(open(sale_and_predictions_pickle_file, "rb"))
    except (OSError, IOError) as e:
        logging.debug("Starting to create joined record list")
        sale_and_predictions_dict = group.join_dicts(sales_records, forecast_records)
        logging.debug("Finished making the list")
        pickle.dump(sale_and_predictions_dict, open(sale_and_predictions_pickle_file, "wb"))
    return sale_and_predictions_dict


def show_graph(sale_and_predictions_list, item_id):
    sale_and_prediction_list_for_item = sale_and_predictions_list.records_list_for_item(item_id)
    sales_dates = [x.date for x in sale_and_prediction_list_for_item]
    sales_quantities = [x.sale_qty for x in sale_and_prediction_list_for_item]
    predicted_quantities = [x.predicted_qty for x in sale_and_prediction_list_for_item]

    graph = quantity_graph.QuantityGraph(
        sales_dates,
        [(sales_quantities, "Sales"), (predicted_quantities, "AGR forecast")],
        "Sales and models for item {0}".format(item_id))
    graph.display_graph()


def log_errors(error_list):
    """
    Log error values to current log output
    :param error_list: List[(str, float, float). List containing the tuples (item_id, float_mae_error, float_mape_error)
    """
    logging.debug("=ERROR LOGGING")
    logging.debug("Number of error items {0}".format(len(error_list)))
    average_abs_error = float(sum([x[1] for x in error_list])) / len(error_list)
    average_percentage_error = float(sum([x[2] for x in error_list])) / len(error_list)

    error_list.sort(key=lambda record: record[2], reverse=True)
    for error in error_list:
        logging.debug("Item {0} had {1}% avg error and {2} abs avg error".format(error[0], error[2], error[1]))

    logging.debug("Average abs forecast error: {0}".format(average_abs_error))
    logging.debug("Average percentage forecast error: {0}".format(average_percentage_error))


def run():
    period = 'M'
    init_logging()

    # Get the data from files and clean it
    sales_records, forecast_records = get_forecast_and_sales_records(period)
    logging.debug("Sales records: {0}, forecast records: {1}".format(len(sales_records), len(forecast_records)))
    sale_and_predictions_dict = join_sales_and_forecasts(sales_records, forecast_records, period)

    for item_id, sales_prediction_records in sale_and_predictions_dict.items():
        # TODO create a model for each item that I want. One agr model and one other model


    agr_model = MockModel(sale_and_predictions_list)
    agr_error_list = agr_model.test()
    log_errors(agr_error_list)

    my_model = NeuralNetwork()
    my_model.train()

    show_graph(sale_and_predictions_list, '7792')


run()
