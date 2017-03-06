import datetime
import logging
import time

import forecast.data.agr as agr_data
import forecast.data.save as save
import forecast.models.machine_learning.neural_network_wrapper as nn_helper
import forecast.graphs.graph_wrapper as graph_wrapper
import forecast.utils.log as forecast_log
from forecast.models.fp_model import FpModel
from forecast.models.machine_learning.neural_network import NeuralNetworkConfig


def run():
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

    # Forecast pro forecasts
    fp_forecasts = {}
    for item_id in item_ids_to_predict:
        fp = FpModel(item_id, sales_records[item_id], fp_forecast_records[item_id], number_of_predictions)
        fp_forecasts_for_item = fp.test()
        fp_forecasts[item_id] = fp_forecasts_for_item
    save.save_prediction_results([fp_forecasts], "AGR", number_of_predictions)

    # Neural Network forecasts
    # Constants
    if period == 'W':
        pass
        # num_input_nodes = 52
    if period == 'M':
        # Values used by empirical paper
        # num_input_nodes = [1, 2, 3, 4, 5]
        # num_hidden_nodes = [0, 1, 3, 5, 7, 9]

        num_input_nodes = [12]
        num_hidden_nodes = [5]

        # num_input_nodes = 12
    else:
        raise Exception("Must use proper period value")

    prediction_cut_date = datetime.datetime(year=2016, month=2, day=1)  # The date FP predicted from (with shift)

    nn_configs = []
    for input_nodes in num_input_nodes:
        for hidden_nodes in num_hidden_nodes:
            hidden_layers = 1 if input_nodes > 0 else 0

            description = "NN. Hidden layers: {hl}, hidden nodes: {hn}, input nodes: {inp}".format(hl=hidden_layers, hn=hidden_nodes, inp=input_nodes)

            nn_configs.append(NeuralNetworkConfig(
                description,
                hidden_layers,
                hidden_nodes,
                input_nodes))

    for nn_config in nn_configs:
        logging.info("== Starting to run model '{description}'".format(description=nn_config.description))
        start_time = time.time()

        nn_forecasts_list = []
        for i in range(10):  # This is done because of random start weights
            nn_forecasts = nn_helper.run_and_predict_nn(
                prediction_cut_date,
                item_ids_to_predict,
                sales_records,
                nn_config.num_hidden_layers,
                nn_config.num_hidden_nodes_per_layer,
                nn_config.num_input_nodes)
            nn_forecasts_list.append(nn_forecasts)
            logging.debug("Finished iteration {iteration} of model".format(iteration=i+1))
        save.save_prediction_results(nn_forecasts_list, nn_config.description, number_of_predictions)
        logging.info("== Finished processing model. Time was {t:.1f} seconds".format(t=time.time()-start_time))

    if should_graph:
        id_to_graph = item_ids_to_predict[0]
        graph_wrapper.show_quantity_graph(sales_records[id_to_graph],
                                          [("FP", fp_forecasts[id_to_graph]),
                                           ("NN", nn_forecasts[id_to_graph])
                                           ],
                                          id_to_graph)


run()
