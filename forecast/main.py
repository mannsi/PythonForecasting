import datetime
import logging

import forecast.data.agr as agr_data
import forecast.data.save as save
import forecast.data.split as splitting
import forecast.data.verification as verification
import forecast.graphs.graph_wrapper as graph_wrapper
import forecast.models.machine_learning.neural_network_wrapper as nn_helper
import forecast.utils.log as forecast_log
from forecast.models.fp_model import fp_model
from forecast.models.machine_learning.neural_network import nn_model


def run():
    forecast_log.init_file_and_console_logging(
        console_log_level=logging.DEBUG,
        file_log_level=logging.INFO,
        file_name="logging_output.txt")

    # Constants
    num_hidden_layers = 1
    num_hidden_nodes_per_layer = 8

    fp_prediction_date = datetime.datetime(year=2016, month=2, day=6)  # The date FP predicted from
    days_to_shift = -fp_prediction_date.day  # Shift by these days so predictions start from the 1. of the month
    prediction_cut_date = datetime.datetime(year=2016, month=2, day=1)  # The date FP predicted from
    max_prediction_date = datetime.datetime(year=2016, month=8, day=1)

    period = 'M'
    if period == 'W':
        number_of_predictions = 26  # How many weeks into the future the models should predict
        num_input_nodes = 52
    if period == 'M':
        number_of_predictions = 6  # How many months into the future the models should predict
        num_input_nodes = 12

    # Get data from files
    sales_records, fp_forecast_records = agr_data.get_data(period, days_to_shift)

    items_to_predict = ['7751']
    # items_to_predict = list(sales_records.keys())

    nn_forecasts = {}
    fp_forecasts = {}

    num_item_models_trained = 0
    for item_id in items_to_predict:
        # Forecast pro forecasts
        fp = fp_model(item_id, sales_records[item_id], fp_forecast_records[item_id], number_of_predictions)
        fp_forecasts_for_item = fp.test()
        fp_forecasts[item_id] = fp_forecasts_for_item

        # Neural network forecasts
        training_records, test_records = splitting.train_test_split(sales_records[item_id], prediction_cut_date)
        verification.verify_training_records_are_sorted(training_records)  # Blows up if training records are not in date order
        training_data = [x.quantity for x in training_records]  # NN only cares about a list of numbers, not dates

        nn = nn_model(item_id, num_hidden_layers, num_hidden_nodes_per_layer, num_input_nodes)
        nn.train(training_data)

        init_values_to_predict = training_data[-nn.num_input_nodes:]  # The last x values of the training set
        nn_forecasts_for_item = nn_helper.get_forecasts_for_nn(item_id, nn, init_values_to_predict, test_records)
        nn_forecasts[item_id] = nn_forecasts_for_item

        num_item_models_trained += 1
        logging.debug("Finished training a model. {0} out of {1} item models done"
                      .format(num_item_models_trained, len(items_to_predict)))

    save.save_prediction_results(fp_forecasts, "AGR", number_of_predictions)
    save.save_prediction_results(nn_forecasts, "My NN", number_of_predictions)

    id_to_graph = items_to_predict[0]
    graph_wrapper.show_quantity_graph(sales_records[id_to_graph],
               [("FP", fp_forecasts[id_to_graph])
                   , ("NN", nn_forecasts[id_to_graph])
                ],
               id_to_graph,
               max_prediction_date)


run()
