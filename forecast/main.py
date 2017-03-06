import datetime
import logging
import time

import forecast.data.agr as agr_data
import forecast.data.save as save
import forecast.data.split as splitting
import forecast.data.verification as verification
import forecast.graphs.graph_wrapper as graph_wrapper
import forecast.models.machine_learning.neural_network_wrapper as nn_helper
import forecast.utils.log as forecast_log
from forecast.models.fp_model import FpModel
from forecast.models.machine_learning.neural_network import NeuralNetwork, NeuralNetworkConfig


def run_and_predict_nn(item_ids_to_predict, sales_records, num_hidden_layers, num_hidden_nodes_per_layer, num_input_nodes):
    # TODO documentation
    # Neural network forecasts
    prediction_cut_date = datetime.datetime(year=2016, month=2, day=1)  # The date FP predicted from (with shift)
    nn_forecasts = {}
    num_item_models_trained = 0
    for item_id in item_ids_to_predict:
        training_records, test_records = splitting.train_test_split(sales_records[item_id], prediction_cut_date)
        verification.verify_training_records_are_sorted(training_records)  # Blows up if training records are not in date order
        training_data = [x.quantity for x in training_records]  # NN only cares about a list of numbers, not dates

        nn = NeuralNetwork(item_id, num_hidden_layers, num_hidden_nodes_per_layer, num_input_nodes)
        nn.train(training_data)

        init_values_to_predict = training_data[-nn.num_input_nodes:]  # The last x values of the training set
        nn_forecasts_for_item = nn_helper.get_forecasts_for_nn(item_id, nn, init_values_to_predict, test_records)
        nn_forecasts[item_id] = nn_forecasts_for_item

        num_item_models_trained += 1
        logging.debug("Finished training a model. {0} out of {1} item models done"
                      .format(num_item_models_trained, len(item_ids_to_predict)))
    return nn_forecasts


def run():
    forecast_log.init_file_and_console_logging(console_log_level=logging.DEBUG, file_log_level=logging.INFO, file_name="logging_output.txt")

    should_graph = False
    period = 'M'
    if period == 'W':
        number_of_predictions = 26  # How many weeks into the future the models should predict
    if period == 'M':
        number_of_predictions = 6  # How many months into the future the models should predict
    else:
        raise Exception("Must use proper period value")

    sales_records, fp_forecast_records = agr_data.data_from_files(period)

    item_ids_to_predict = ['7751']
    # items_to_predict = list(sales_records.keys())

    # Forecast pro forecasts
    fp_forecasts = {}
    for item_id in item_ids_to_predict:
        fp = FpModel(item_id, sales_records[item_id], fp_forecast_records[item_id], number_of_predictions)
        fp_forecasts_for_item = fp.test()
        fp_forecasts[item_id] = fp_forecasts_for_item
    save.save_prediction_results(fp_forecasts, "AGR", number_of_predictions)

    # Neural Network forecasts
    # Constants
    if period == 'W':
        pass
        # num_input_nodes = 52
    if period == 'M':
        # Values used by empirical paper
        # num_input_nodes = [1, 2, 3, 4, 5]
        # num_hidden_nodes = [0, 1, 3, 5, 7, 9]

        num_input_nodes = [3, 12]
        num_hidden_nodes = [5]

        # num_input_nodes = 12
    else:
        raise Exception("Must use proper period value")

    nn_configs = []
    for input_nodes in num_input_nodes:
        for hidden_nodes in num_hidden_nodes:
            hidden_layers = 1 if input_nodes > 0 else 0

            description = "NN. Hidden layers: {hl}, hidden nodes: {hn}, input nodes: {inp}".format(hl = hidden_layers, hn=hidden_nodes, inp=input_nodes)

            nn_configs.append(NeuralNetworkConfig(
                description,
                hidden_layers,
                hidden_nodes,
                input_nodes))

    for nn_config in nn_configs:
        logging.info("== Starting to run model '{description}'".format(description=nn_config.description))
        start_time = time.time()
        nn_forecasts = run_and_predict_nn(
            item_ids_to_predict,
            sales_records,
            nn_config.num_hidden_layers,
            nn_config.num_hidden_nodes_per_layer,
            nn_config.num_input_nodes)
        save.save_prediction_results(nn_forecasts, nn_config.description, number_of_predictions)
        logging.info("== Finished processing model. Time was {t}".format(t=time.time()-start_time))

    if should_graph:
        id_to_graph = item_ids_to_predict[0]
        graph_wrapper.show_quantity_graph(sales_records[id_to_graph],
                                          [("FP", fp_forecasts[id_to_graph]),
                                           ("NN", nn_forecasts[id_to_graph])
                                           ],
                                          id_to_graph)


run()
