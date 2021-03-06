import datetime
import logging
import time
import numpy
import sys

import forecast.data.agr as agr_data
import forecast.models.machine_learning.neural_network_wrapper as nn_helper
import forecast.utils.log as forecast_log
import forecast.data.split as splitting
import forecast.models.verification.error_calculations as error_calculations
import forecast.data.preprocessing as preprocessing
from forecast.data.structures import ItemForecastResult
from forecast.models.fp_model import FpModel
from forecast.models.machine_learning.neural_network import NeuralNetworkConfig
from forecast.models.machine_learning.neural_network import NeuralNetwork


def run():
    # logging.warning("RUN DESCRIPTION")
    # fix random seed for reproducibility
    seed = 7
    numpy.random.seed(seed)

    sales_records, fp_forecast_records = agr_data.data_from_files()

    item_ids_to_predict = list(sales_records.keys())
    # item_ids_to_predict = ['24585']

    # Forecast pro forecasts
    fp_weighted_errors = {}
    for item_id in item_ids_to_predict:
        fp = FpModel(item_id, sales_records[item_id], fp_forecast_records[item_id], 6)
        fp_forecasts_for_item = fp.get_predictions()
        fp_weighted_errors[item_id] = error_calculations.get_errors_for_item(fp_forecasts_for_item)

    # Neural Network forecasts

    # Nodes from initial trial run
    # num_input_nodes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    # num_hidden_nodes = [3, 5, 7, 9, 11]

    # Nodes after seeing the best combinations from the initial trial run
    num_input_nodes = [12, 13, 14, 15]
    num_hidden_nodes = [9, 11]
    prediction_cut_date = datetime.datetime(year=2016, month=2, day=1)  # The date FP predicted from (with shift)
    num_times_to_train_each_nn = 10
    nn_configs = get_nn_configs(num_hidden_nodes, num_input_nodes)
    preprocessing_method = 'DIFF'

    item_counter = 0
    for item_id in item_ids_to_predict:
        results_for_item = []
        item_counter += 1
        config_counter = 0
        item_start_time = time.time()
        for nn_config in nn_configs:
            config_counter += 1
            config_start_time = time.time()

            # Train the model
            training_data, testing_data = splitting.train_test_split(sales_records[item_id], prediction_cut_date)

            if preprocessing_method == 'MA':
                training_data, testing_data = preprocessing.moving_average(training_data, testing_data)
            elif preprocessing_method == 'DIFF':
                last_training_value = training_data[-1]  # Used with diff prediction to get actual predicted value
                training_data, testing_data = preprocessing.diff(training_data, testing_data)

            training_error_sum = 0
            for i in range(num_times_to_train_each_nn):
                nn = NeuralNetwork(nn_config.num_hidden_nodes_per_layer, nn_config.num_input_nodes)
                training_error_sum += numpy.sqrt(nn.train(training_data))
            training_error = float(training_error_sum) / num_times_to_train_each_nn

            # Get forecasts
            init_values_to_predict = training_data[-nn.num_input_nodes:]  # The last x values of the training set
            if preprocessing_method == 'DIFF':
                nn_forecasts_for_item = nn_helper.get_forecasts_for_nn_with_diff(item_id, nn, init_values_to_predict,
                                                                                 last_training_value, testing_data)
            else:
                nn_forecasts_for_item = nn_helper.get_forecasts_for_nn(item_id, nn, init_values_to_predict,
                                                                       testing_data)

            # Sum up results
            weighted_error, list_of_errors_by_month = error_calculations.get_errors_for_item(nn_forecasts_for_item)
            result = ItemForecastResult(item_id, nn_config.num_hidden_nodes_per_layer, nn_config.num_input_nodes, 1, training_error, weighted_error, list_of_errors_by_month)
            results_for_item.append(result)

            if len(nn_configs) > 1:
                time_for_config = int(time.time() - config_start_time)
                logging.debug("Finished config setting nr {counter} out of {num_configs} for item {item}. Took {t} sec".
                              format(counter=config_counter, item=item_id, num_configs=len(nn_configs), t=time_for_config))

        # Log results for item
        results_for_item.sort(key=lambda x: x.training_error)
        best_result = results_for_item[0]
        forecast_log.log_best_result_for_item(best_result, fp_weighted_errors, item_id)
        forecast_log.log_summary_for_item(item_id, results_for_item)

        time_for_item = int(time.time() - item_start_time)
        logging.debug("Finished processing item {ic} out of {total}. Took {t} seconds"
                      .format(ic=item_counter, total=len(item_ids_to_predict), t=time_for_item))


def get_nn_configs(num_hidden_nodes, num_input_nodes):
    nn_configs = []
    for input_nodes in num_input_nodes:
        for hidden_nodes in num_hidden_nodes:

            description = "NN.hidden nodes: {hn}, input nodes: {inp}".format(hn=hidden_nodes, inp=input_nodes)

            nn_configs.append(NeuralNetworkConfig(
                description,
                hidden_nodes,
                input_nodes))
    return nn_configs


if __name__ == "__main__":
    forecast_log.init_file_and_console_logging(
        console_log_level=logging.DEBUG,
        details_file_name="logging_details.txt",
        summary_file_name="logging_summary.txt")
    run()
