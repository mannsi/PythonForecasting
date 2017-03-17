import datetime
import logging
import time
import numpy

import forecast.data.agr as agr_data
import forecast.data.save as save
import forecast.models.machine_learning.neural_network_wrapper as nn_helper
import forecast.graphs.graph_wrapper as graph_wrapper
import forecast.utils.log as forecast_log
import forecast.data.split as splitting
from forecast.models.fp_model import FpModel
from forecast.models.machine_learning.neural_network import NeuralNetworkConfig
from forecast.models.machine_learning.neural_network import NeuralNetwork
import forecast.models.verification.error_calculations as error_calculations


def run():
    # fix random seed for reproducibility
    seed = 7
    numpy.random.seed(seed)

    forecast_log.init_file_and_console_logging(
        console_log_level=logging.DEBUG,
        details_file_name="logging_details.txt",
        summary_file_name="logging_summary.txt")

    should_graph = False
    period = 'M'
    if period == 'W':
        number_of_predictions = 26  # How many weeks into the future the models should predict
    if period == 'M':
        number_of_predictions = 6  # How many months into the future the models should predict
    else:
        raise Exception("Must use proper period value")

    sales_records, fp_forecast_records = agr_data.data_from_files(period)

    # item_ids_to_predict = ['7751']
    item_ids_to_predict = list(sales_records.keys())
    # num_items_to_predict = 10
    # item_ids_to_predict = list(sales_records.keys())[:num_items_to_predict]

    # Forecast pro forecasts
    fp_forecasts = {}
    fp_weighted_errors = {}
    for item_id in item_ids_to_predict:
        fp = FpModel(item_id, sales_records[item_id], fp_forecast_records[item_id], number_of_predictions)
        fp_forecasts_for_item = fp.test()
        fp_weighted_errors[item_id] = error_calculations.get_errors_for_item(fp_forecasts_for_item)
        fp_forecasts[item_id] = fp_forecasts_for_item
    # save.save_prediction_results([fp_forecasts], "AGR", number_of_predictions)

    # Neural Network forecasts
    # Constants
    if period == 'W':
        pass
        # num_input_nodes = 52
    if period == 'M':
        # Values used by empirical paper
        num_input_nodes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        # num_input_nodes = [1, 2, 3, 4, 5]
        num_hidden_nodes = [1, 3, 5, 7, 9]

        # num_input_nodes = [12]
        # num_hidden_nodes = [5]

        # num_input_nodes = 12
    else:
        raise Exception("Must use proper period value")

    prediction_cut_date = datetime.datetime(year=2016, month=2, day=1)  # The date FP predicted from (with shift)

    nn_configs = get_nn_configs(num_hidden_nodes, num_input_nodes)

    item_counter = 0
    for item_id in item_ids_to_predict:
        results_for_item = []
        counter = 0
        item_start_time = time.time()
        for nn_config in nn_configs:
            counter += 1
            config_start_time = time.time()

            # Train the model
            training_records, test_records = splitting.train_test_split(sales_records[item_id], prediction_cut_date)
            training_data = [x.quantity for x in training_records]  # NN only cares about a list of numbers, not dates
            nn = NeuralNetwork(nn_config.num_hidden_layers, nn_config.num_hidden_nodes_per_layer,
                               nn_config.num_input_nodes)
            nn.train(training_data)

            # Get forecasts
            init_values_to_predict = training_data[-nn.num_input_nodes:]  # The last x values of the training set
            nn_forecasts_for_item = nn_helper.get_forecasts_for_nn(item_id, nn, init_values_to_predict, test_records)

            # Sum up results
            weighted_error, list_of_errors_by_month = error_calculations.get_errors_for_item(nn_forecasts_for_item)
            result = ItemForecastResult()
            result.item_id = item_id
            result.hidden_nodes = nn_config.num_hidden_nodes_per_layer
            result.input_nodes = nn_config.num_input_nodes
            result.weighted_error = weighted_error
            result.errors_per_month = list_of_errors_by_month

            results_for_item.append(result)
            if len(nn_configs) > 1:
                t = int(time.time() - config_start_time)
                logging.debug("Finished config setting nr {counter} out of {num_configs} for item {item}. Took {t} sec".
                              format(counter=counter, item=item_id, num_configs=len(nn_configs), t=t))

        results_for_item.sort(key=lambda x: x.weighted_error)

        best_result = results_for_item[0]
        logging.debug("Best result for item {iid} by weighted error:")
        logging.warning(
            "== Result for {iid}. Best WE:{we:.2f}, FP_WE: {fp_we:.2f},  HN:{hn}, IN:{inp}, ByMonth:({by_month})".
            format(we=best_result.weighted_error,
                   hn=best_result.hidden_nodes,
                   inp=best_result.input_nodes,
                   iid=item_id,
                   fp_we=fp_weighted_errors[best_result.item_id][0],
                   by_month=','.join('{:.2f}'.format(x) for x in best_result.errors_per_month)))

        t = int(time.time() - item_start_time)
        logging.debug("Results for {iid} in decreasing order. Took {t} seconds".format(iid=item_id, t=t))
        for result in results_for_item:
            logging.debug("We:{we:.2f}. HN:{hn}, IN:{inp}".
                          format(we=result.weighted_error, hn=result.hidden_nodes, inp=result.input_nodes))
        logging.debug(
            "Finished processing item {ic} out of {total}".format(ic=item_counter, total=len(item_ids_to_predict)))
            # for nn_config in nn_configs:
            #     logging.info("== Starting to run model '{description}'".format(description=nn_config.description))
            #     start_time = time.time()
            #
            #     nn_forecasts_list = []
            #
            #
            #
            #     for i in range(10):  # This is done because of random start weights
            #         iteration_start_time = time.time()
            #         nn_forecasts = nn_helper.run_and_predict_nn(
            #             prediction_cut_date,
            #             item_ids_to_predict,
            #             sales_records,
            #             nn_config.num_hidden_layers,
            #             nn_config.num_hidden_nodes_per_layer,
            #             nn_config.num_input_nodes)
            #         nn_forecasts_list.append(nn_forecasts)
            #         logging.debug("Finished iteration {iteration} of model. Time was {t:.1f} seconds".format(iteration=i+1, t=time.time()-iteration_start_time))
            #     save.save_prediction_results(nn_forecasts_list, nn_config.description, number_of_predictions)
            #     logging.info("== Finished processing model. Time was {t:.1f} seconds".format(t=time.time()-start_time))

            # if should_graph:
            #     id_to_graph = item_ids_to_predict[0]
            #     graph_wrapper.show_quantity_graph(sales_records[id_to_graph],
            #                                       [("FP", fp_forecasts[id_to_graph]),
            #                                        ("NN", nn_forecasts[id_to_graph])
            #                                        ],
            #                                       id_to_graph)


class ItemForecastResult:
    def __init__(self):
        self.item_id = ''
        self.hidden_nodes = 0
        self.input_nodes = 0
        self.hidden_layers = 1
        self.weighted_error = 0
        self.errors_per_month = []


def get_nn_configs(num_hidden_nodes, num_input_nodes):
    nn_configs = []
    for input_nodes in num_input_nodes:
        for hidden_nodes in num_hidden_nodes:
            hidden_layers = 1 if input_nodes > 0 else 0

            description = "NN. Hidden layers: {hl}, hidden nodes: {hn}, input nodes: {inp}".format(hl=hidden_layers,
                                                                                                   hn=hidden_nodes,
                                                                                                   inp=input_nodes)

            nn_configs.append(NeuralNetworkConfig(
                description,
                hidden_layers,
                hidden_nodes,
                input_nodes))
    return nn_configs


run()
