import logging
import os
import pickle
from typing import List, Dict, Tuple
import datetime
import math
import random

import forecast.models.verification.error_calculations as error_calculations
import forecast.IO.file_reader as file_reader
import forecast.graphs.quantitygraph as quantity_graph
import forecast.data_manipulation.group as group
import forecast.data_manipulation.splitting as splitting
import forecast.data_manipulation.clean as clean
import forecast.models.machine_learning.neural_network_helper as nn_helper
from forecast.models.agr.mock_model import MockModel
from forecast.models.machine_learning.neural_network import NeuralNetwork
from forecast.data_structures.records import ItemDateQuantityRecord
from forecast.data_structures.output import PredictionRecord


def init_logging(log_level):
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')


def get_forecast_and_sales_records(
        group_by: str,
        days_to_shift: int) -> Tuple[Dict[str, List[ItemDateQuantityRecord]], Dict[str, List[ItemDateQuantityRecord]]]:
    """
    Gets the tuple grouped_sales_records, grouped_forecast_records
    :param days_to_shift:
    :param group_by: 'W' or 'M'
    :return: ({item_id: list of sales records}, {item_id: list of forecast records})
    """
    forecast_value_pickle_file = group_by + "forecast_values.pickle"
    sales_values_pickle_file = group_by + "sales_values.pickle"

    try:
        grouped_forecast_records = pickle.load(open(forecast_value_pickle_file, "rb"))
        logging.info("Loading forecast list from memory")
    except (OSError, IOError) as e:
        forecast_file_abs_path = os.path.abspath(os.path.join("files", "forecast_values.txt"))
        forecast_records = file_reader.get_sample_forecast_values(forecast_file_abs_path)

        # Shift the data so it fits nicely f.x. to weeks or months
        for item_id, records_for_item in forecast_records.items():
            clean.shift_data_by_days(records_for_item, days_to_shift)

        grouped_forecast_records = group_item_quantity_records(forecast_records, group_by)
        grouped_forecast_records = clean.remove_nan_quantity_values(grouped_forecast_records)
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

        # Shift the data so it fits nicely f.x. to weeks or months
        for item_id, records_for_item in sales_records.items():
            clean.shift_data_by_days(records_for_item, days_to_shift)

        grouped_sales_records = group_item_quantity_records(sales_records, group_by)
        grouped_sales_records = clean.remove_nan_quantity_values(grouped_sales_records)

        # First record is not a whole month. That is why we remove it
        grouped_sales_records = clean.drop_first_values_for_each_item(grouped_sales_records)
        pickle.dump(grouped_sales_records, open(sales_values_pickle_file, "wb"))
        num_sales_records = sum([len(item_records) for item_id, item_records in sales_records.items()])
        logging.info("Found {0} items with {1} number of sales values and grouped them down to {2}"
                     .format(len(sales_records), num_sales_records, len(grouped_sales_records)))

    return grouped_sales_records, grouped_forecast_records


def group_item_quantity_records(
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


def show_graph(sales_values: List[ItemDateQuantityRecord],
               prediction_lists: List[Tuple[str, List[PredictionRecord]]],
               item_id,
               max_prediction_date: datetime.datetime):
    graph_line_list = []

    sales_values = [x for x in sales_values if x.date <= max_prediction_date]
    sales_dates = [x.date for x in sales_values]
    sales_quantities = [x.quantity for x in sales_values]
    graph_line_list.append((sales_quantities, "Sales"))

    for prediction_list in prediction_lists:
        prediction_name = prediction_list[0]
        predicted_records = prediction_list[1]
        generated_prediction_values = []
        for sales_value in sales_values:
            sale_date_found = False
            for predicted_record in predicted_records:
                if sales_value.date == predicted_record.date:
                    # This if for sanity checking
                    if sales_value.quantity != predicted_record.qty:
                        raise Exception("Why is the sales value and qty from prediction record not the same ?!?!?!?!")

                    generated_prediction_values.append(predicted_record.predicted_qty)
                    sale_date_found = True
            if not sale_date_found:
                generated_prediction_values.append(None)

        graph_line_list.append((generated_prediction_values, prediction_name))

    graph = quantity_graph.QuantityGraph(
        sales_dates,
        graph_line_list,
        "Sales and models for item {0}".format(item_id))
    graph.display_graph()


def log_errors(predictions: Dict[str, List[PredictionRecord]],
               model_name: str,
               steps_to_measure_accuracy: List[int],
               steps_name: List[str]):
    """
    Log error values to current log output
    :param steps_to_measure_accuracy: list of indexes where we want to output the accuracy of the model
    :param model_name: the name of the model being used
    :param predictions:
    """

    error_list = error_calculations.average_percentage_error(predictions, steps_to_measure_accuracy)

    for i in range(len(error_list)):
        error = error_list[i]
        step_name = steps_name[i]
        logging.info("Average percentage error for {step_name}: {error_val:.2f}% using model {model}"
                     .format(step_name=step_name, error_val=error, model=model_name))


def get_data(period, date_shift):
    # Get the data from files and clean it
    sales_records, forecast_pro_forecast_records = get_forecast_and_sales_records(period, date_shift)
    logging.debug("Sales records: {0}, forecast records: {1}"
                  .format(len(sales_records), len(forecast_pro_forecast_records)))
    sales_records, forecast_pro_forecast_records = clean.remove_items_with_no_predictions(sales_records,
                                                                                          forecast_pro_forecast_records)
    logging.debug("Sales records: {0}, forecast records: {1} after cleaning"
                  .format(len(sales_records), len(forecast_pro_forecast_records)))

    return sales_records, forecast_pro_forecast_records


def verify_training_records_are_sorted(training_records):
    is_sorted = _is_training_data_sorted(training_records)
    if not is_sorted:
        raise Exception("Training data for NN is not sorted by date !")


def run():
    init_logging(logging.INFO)

    # TODO output the std dev of the prediction stuff. Read and try to figure out

    # Constants
    num_hidden_layers = 1
    num_hidden_nodes_per_layer = 8

    fp_prediction_date = datetime.datetime(year=2016, month=2, day=6)  # The date FP predicted from
    days_to_shift = -fp_prediction_date.day  # Shift by these days so predictions start from the 1. of the month
    prediction_cut_date = datetime.datetime(year=2016, month=2, day=1)  # The date FP predicted from
    max_prediction_date = datetime.datetime(year=2016, month=8, day=1)

    period = 'M'
    if period == 'W':
        steps_to_measure_accuracy = [4, 12, 26]  # Points when precision is calculated and logged
        step_name = ["1 month prediction", "3 month prediction",
                     "6 month prediction"]  # Points when precision is calculated and logged
        number_of_predictions = 26  # How many weeks into the future the models should predict
        num_input_nodes = 52
    if period == 'M':
        steps_to_measure_accuracy = [1, 3, 6]  # Points when precision is calculated and logged
        step_name = ["1 month prediction", "3 month prediction",
                     "6 month prediction"]  # Points when precision is calculated and logged
        number_of_predictions = 6  # How many months into the future the models should predict
        num_input_nodes = 12

    # Get data from files
    sales_records, fp_forecast_records = get_data(period, days_to_shift)

    items_to_predict = ['7751']
    # items_to_predict = list(sales_records.keys())

    nn_forecasts = {}
    fp_forecasts = {}

    num_item_models_trained = 0
    for item_id in items_to_predict:
        # Forecast pro forecasts
        fp_model = MockModel(item_id, sales_records[item_id], fp_forecast_records[item_id], number_of_predictions)
        fp_forecasts_for_item = fp_model.test()
        fp_forecasts[item_id] = fp_forecasts_for_item

        # Neural network forecasts
        # training_records, test_records = splitting.train_test_split(sales_records[item_id], prediction_cut_date)
        # verify_training_records_are_sorted(training_records)  # Blows up if training records are not in date order
        # training_data = [x.quantity for x in training_records]  # NN only cares about a list of numbers, not dates
        #
        # nn = NeuralNetwork(item_id, num_hidden_layers, num_hidden_nodes_per_layer, num_input_nodes)
        # nn.train(training_data)
        #
        # init_values_to_predict = training_data[-nn.num_input_nodes:]  # The last x values of the training set
        # nn_forecasts_for_item = nn_helper.get_forecasts_for_nn(item_id, nn, init_values_to_predict, test_records)
        # nn_forecasts[item_id] = nn_forecasts_for_item
        #
        # num_item_models_trained += 1
        # logging.info("Finished training a model. {0} out of {1} item models done"
        #              .format(num_item_models_trained, len(items_to_predict)))

    log_errors(fp_forecasts, "AGR", steps_to_measure_accuracy, step_name)
    # log_errors(nn_forecasts, "My NN", steps_to_measure_accuracy, step_name)

    id_to_graph = items_to_predict[0]
    show_graph(sales_records[id_to_graph],
               [("FP", fp_forecasts[id_to_graph])
                   # , ("NN", nn_forecasts[id_to_graph])
                ],
               id_to_graph,
               max_prediction_date)


def _is_training_data_sorted(training_data):
    previous_date = None
    for training_record in training_data:
        if previous_date is None:
            previous_date = training_record.date
            continue

        if training_record.date < previous_date:
            return False

    return True


run()
