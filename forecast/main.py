import logging
import os
import pickle
from typing import List, Dict
import datetime

import forecast.IO.file_reader as file_reader
import forecast.graphs.quantitygraph as quantity_graph
import forecast.data_manipulation.group as group
import forecast.data_manipulation.splitting as splitting
import forecast.models.verification.model_accuracy as model_accuracy
import forecast.data_manipulation.clean as clean
from forecast.models.agr.mock_model import MockModel
from forecast.models.machine_learning.neural_network import NeuralNetwork
from forecast.data_structures.records import ItemDateQuantityRecord
from forecast.data_structures.output import PredictionOutput


def init_logging(log_level):
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')


def get_forecast_and_sales_records(group_by):
    """
    Gets the tuple grouped_sales_records, grouped_forecast_records
    :param group_by: string
    :return: ({item_id: list of ItemDateQuantityRecord}, {item_id: list of records..ItemDateQuantityRecord})
    """
    forecast_value_pickle_file = group_by + "forecast_values.pickle"
    sales_values_pickle_file = group_by + "sales_values.pickle"

    try:
        grouped_forecast_records = pickle.load(open(forecast_value_pickle_file, "rb"))
        logging.info("Loading forecast list from memory")
    except (OSError, IOError) as e:
        forecast_file_abs_path = os.path.abspath(os.path.join("files", "forecast_values.txt"))
        forecast_records = file_reader.get_sample_forecast_values(forecast_file_abs_path)
        grouped_forecast_records = group_item_quantity_records(forecast_records, group_by)
        grouped_forecast_records = clean.remove_nan_quantity_values(grouped_forecast_records)
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
        grouped_sales_records = group_item_quantity_records(sales_records, group_by)
        grouped_sales_records = clean.remove_nan_quantity_values(grouped_sales_records)
        grouped_sales_records = clean.drop_first_and_last_values_for_each_item(grouped_sales_records)
        pickle.dump(grouped_sales_records, open(sales_values_pickle_file, "wb"))

        num_sales_records = sum([len(item_records) for item_id, item_records in sales_records.items()])
        logging.info("Found {0} items with {1} number of sales values and grouped them down to {2}"
                      .format(len(sales_records), num_sales_records, len(grouped_sales_records)))

    return grouped_sales_records, grouped_forecast_records


def group_item_quantity_records(item_quantity_records, group_by):
    """

    :param item_quantity_records: {item_id: list of ItemDateQuantityRecord}
    :param group_by: string
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


def join_sales_and_forecasts(sales_records: List[ItemDateQuantityRecord],
                             forecast_records: List[ItemDateQuantityRecord], period):
    sale_and_predictions_pickle_file = period + "sale_and_predictions_list.pickle"
    try:
        sale_and_predictions_dict = pickle.load(open(sale_and_predictions_pickle_file, "rb"))
        logging.info("Loading joined sales and forecast list from memory")
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


def log_errors(prediction_outputs: Dict[str, List[PredictionOutput]], model_name, num_predictions_per_item):
    """
    Log error values to current log output
    :param prediction_outputs:
    :param error_list: Dict{item_id: List(date, sale_qty, predicted_qty, mape)}
    """

    # TODO
    logging.debug("Details for model {model}".format(model=model_name))
    # prediction_outputs_for_all_items = []  # List of prediction output tuples
    # for item_id, prediction_outputs in prediction_outputs.items():
    #     # logging.debug("Item {0} had {1}% avg error and {2} abs avg error".format(error[0], error[2], error[1]))
    #     prediction_outputs_for_all_items.append(prediction_outputs)
    #     max_num_output_predictions = max(max_num_output_predictions, len(prediction_outputs))

    average_error_values_per_prediction = []

    for i in range(num_predictions_per_item):
        prediction_values_for_date = [x[i] for x in prediction_outputs.values()]
        unique_prediction_dates = len(set([x.date for x in prediction_values_for_date]))
        if unique_prediction_dates != 1:
            raise Exception("All predictions should be for the same date. Something is wrong with the data")
        all_errors_for_this_dates_prediction = [x.error for x in prediction_values_for_date]
        average_error_for_prediction = float(sum(all_errors_for_this_dates_prediction)) / len(all_errors_for_this_dates_prediction)
        average_error_values_per_prediction.append(average_error_for_prediction)
        logging.info("Average percentage error for prediction {prediction_description} is {av_error:.2f}"
                     .format(prediction_description=i+1, av_error=average_error_for_prediction))


def run():
    # Start by evaluating predictions for 4 weeks, but have it as a parameter

    # TODO output the std dev of the prediction stuff. Read and try to figure out
    period = 'W'
    number_of_predictions = 4
    init_logging(logging.INFO)

    forecast_pro_prediction_date = datetime.datetime(year=2016, month=2, day=6)

    # Get the data from files and clean it
    sales_records, forecast_records = get_forecast_and_sales_records(period)
    logging.debug("Sales records: {0}, forecast records: {1}".format(len(sales_records), len(forecast_records)))
    sales_records, forecast_records = clean.remove_items_with_no_predictions(sales_records, forecast_records)

    logging.debug("Sales records: {0}, forecast records: {1} after cleaning".format(len(sales_records), len(forecast_records)))
    sale_and_predictions_dict = join_sales_and_forecasts(sales_records, forecast_records, period)
    logging.info("Joined sales and forecast list has {0} items".format(len(sale_and_predictions_dict)))

    agr_models_error_dict = {}
    # my_models_error_list = []  # TODO change to other data structure
    for item_id, sales_prediction_records in sale_and_predictions_dict.items():
        agr_model = MockModel(item_id, sales_prediction_records, number_of_predictions)
        agr_error_list_for_item = agr_model.test()
        agr_models_error_dict[item_id] = agr_error_list_for_item

        # sales_records_for_item = sales_records[item_id]
        # training_data, test_data, test_data_answers = splitting.to_train_and_test_date_split(sales_records_for_item,forecast_pro_prediction_date)
        #
        # logging.debug("Num training data: {0}, test data: {1}, test data answers: {2}". format(len(training_data), len(test_data), len(test_data_answers)))
        # nn = NeuralNetwork(item_id, period)
        # nn.train(training_data)
        # nn_mae, nn_mape, nn_sales_prediction_records = model_accuracy.accuracy(nn, test_data, test_data_answers)
        #
        # my_models_error_list.append((item_id, nn_mae, nn_mape))

    log_errors(agr_models_error_dict, "AGR", number_of_predictions)
    # log_errors(my_models_error_list, "My NN")

    item_id_to_graph = '7792'
    show_graph(sale_and_predictions_dict[item_id_to_graph], item_id_to_graph)


run()
