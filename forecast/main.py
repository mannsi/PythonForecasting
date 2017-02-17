import logging
import os
import pickle
from typing import List
import datetime

import forecast.IO.file_reader as file_reader
import forecast.data_structures.records as records
import forecast.graphs.quantitygraph as quantity_graph
import forecast.data_manipulation.group as group
import forecast.data_manipulation.splitting as splitting
import forecast.models.verification.model_accuracy as model_accuracy
import forecast.data_manipulation.clean as clean
from forecast.models.agr.mock_model import MockModel
from forecast.models.machine_learning.neural_network import NeuralNetwork
from forecast.data_structures.records import ItemDateQuantityRecord


def init_logging(log_level):
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')


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
        logging.info("Loading forecast list from memory")
    except (OSError, IOError) as e:
        forecast_file_abs_path = os.path.abspath(os.path.join("files", "forecast_values.txt"))
        forecast_records = file_reader.get_sample_forecast_values(forecast_file_abs_path)
        forecast_records = clean.remove_nan_quantity_values(forecast_records)
        grouped_forecast_records = group_item_quantity_records(forecast_records, group_by)
        grouped_forecast_records = clean.drop_first_and_last_values_for_each_item(grouped_forecast_records)
        pickle.dump(grouped_forecast_records, open(forecast_value_pickle_file, "wb"))

        num_forecast_records = sum([len(item_records) for item_id, item_records in forecast_records.items()])
        logging.info("Found {0} items with {1} number of forecast values and grouped them down to {2}"
                      .format(len(forecast_records), num_forecast_records, len(grouped_forecast_records)))

    try:
        grouped_sales_records = pickle.load(open(sales_values_pickle_file, "rb"))
        logging.info("Loading sales list from memory")
    except (OSError, IOError) as e:
        sales_file_abs_path = os.path.abspath(os.path.join("files", "histories_sales.txt"))
        sales_records = file_reader.get_sample_history_sales_values(sales_file_abs_path)
        sales_records = clean.remove_nan_quantity_values(sales_records)
        grouped_sales_records = group_item_quantity_records(sales_records, group_by)
        grouped_sales_records = clean.drop_first_and_last_values_for_each_item(grouped_sales_records)
        pickle.dump(grouped_sales_records, open(sales_values_pickle_file, "wb"))

        num_sales_records = sum([len(item_records) for item_id, item_records in sales_records.items()])
        logging.info("Found {0} items with {1} number of sales values and grouped them down to {2}"
                      .format(len(sales_records), num_sales_records, len(grouped_sales_records)))

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


def join_sales_and_forecasts(sales_records: List[ItemDateQuantityRecord],
                             forecast_records: List[ItemDateQuantityRecord], period):
    sale_and_predictions_pickle_file = period + "sale_and_predictions_list.pickle"
    try:
        sale_and_predictions_dict = pickle.load(open(sale_and_predictions_pickle_file, "rb"))
    except (OSError, IOError) as e:
        logging.info("Starting to create joined record list")
        sale_and_predictions_dict = group.join_dicts(sales_records, forecast_records)
        logging.info("Finished making the list")
        pickle.dump(sale_and_predictions_dict, open(sale_and_predictions_pickle_file, "wb"))
    return sale_and_predictions_dict


def show_graph(sale_and_predictions_list, item_id):
    sales_dates = [x.date for x in sale_and_predictions_list]
    sales_quantities = [x.sale_qty for x in sale_and_predictions_list]
    predicted_quantities = [x.predicted_qty for x in sale_and_predictions_list]

    graph = quantity_graph.QuantityGraph(
        sales_dates,
        [(sales_quantities, "Sales"), (predicted_quantities, "AGR forecast")],
        "Sales and models for item {0}".format(item_id))
    graph.display_graph()


def log_errors(error_list, model_name):
    """
    Log error values to current log output
    :param error_list: List[(str, float, float). List containing the tuples (item_id, float_mae_error, float_mape_error)
    """
    average_abs_error = float(sum([x[1] for x in error_list])) / len(error_list)
    average_percentage_error = float(sum([x[2] for x in error_list])) / len(error_list)

    error_list.sort(key=lambda record: record[2], reverse=True)
    logging.debug("Details for model {model}".format(model=model_name))
    for error in error_list:
        logging.debug("Item {0} had {1}% avg error and {2} abs avg error".format(error[0], error[2], error[1]))

    logging.info("Log for model {model}=> Num error items: {num_items}, mae: {mae}, mape:{mape}"
                 .format(num_items=len(error_list), mae=average_abs_error, mape=average_percentage_error, model=model_name))


def run():
    period = 'M'
    init_logging(logging.INFO)

    # Get the data from files and clean it
    sales_records, forecast_records = get_forecast_and_sales_records(period)
    logging.info("Sales records: {0}, forecast records: {1}".format(len(sales_records), len(forecast_records)))
    sales_records, forecast_records = clean.remove_items_with_no_predictions(sales_records, forecast_records)
    logging.info("Sales records: {0}, forecast records: {1} after cleaning".format(len(sales_records), len(forecast_records)))
    sale_and_predictions_dict = join_sales_and_forecasts(sales_records, forecast_records, period)
    logging.info("Joined sales and forecast list has {0} items".format(len(sale_and_predictions_dict)))

    agr_models_error_list = []
    my_models_error_list = []
    for item_id, sales_prediction_records in sale_and_predictions_dict.items():
        agr_model = MockModel(item_id, sales_prediction_records)
        agr_models_error_list.append(agr_model.test())

        sales_records_for_item = sales_records[item_id]
        training_data, test_data, test_data_answers = splitting.to_train_and_test_date_split(sales_records_for_item,
                                                                                             datetime.datetime(
                                                                                                 year=2016, month=2,
                                                                                                 day=6))

        logging.debug("Num training data: {0}, test data: {1}, test data answers: {2}". format(len(training_data), len(test_data), len(test_data_answers)))
        nn = NeuralNetwork(item_id)
        nn.train(training_data)
        nn_mae, nn_mape, nn_sales_prediction_records = model_accuracy.accuracy(nn, test_data, test_data_answers)

        my_models_error_list.append((item_id, nn_mae, nn_mape))

    log_errors(agr_models_error_list, "AGR")
    log_errors(my_models_error_list, "My NN")

    item_id_to_graph = '7792'
    show_graph(sale_and_predictions_dict[item_id_to_graph], item_id_to_graph)


run()
