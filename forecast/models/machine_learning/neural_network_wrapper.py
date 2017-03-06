import logging


import forecast.data.split as splitting
import forecast.data.verification as verification
import forecast.models.verification.error_calculations as error_calculations
from forecast.data.structures import PredictionRecord
from forecast.models.machine_learning.neural_network import NeuralNetwork


def run_and_predict_nn(prediction_cut_date, item_ids_to_predict, sales_records, num_hidden_layers, num_hidden_nodes_per_layer, num_input_nodes):
    # TODO documentation
    # Neural network forecasts

    nn_forecasts = {}
    num_item_models_trained = 0
    for item_id in item_ids_to_predict:
        training_records, test_records = splitting.train_test_split(sales_records[item_id], prediction_cut_date)
        verification.verify_training_records_are_sorted(training_records)  # Blows up if training records are not in date order
        training_data = [x.quantity for x in training_records]  # NN only cares about a list of numbers, not dates

        nn = NeuralNetwork(item_id, num_hidden_layers, num_hidden_nodes_per_layer, num_input_nodes)
        nn.train(training_data)

        init_values_to_predict = training_data[-nn.num_input_nodes:]  # The last x values of the training set
        nn_forecasts_for_item = get_forecasts_for_nn(item_id, nn, init_values_to_predict, test_records)
        nn_forecasts[item_id] = nn_forecasts_for_item

        num_item_models_trained += 1
        logging.debug("Finished training a model. {0} out of {1} item models done"
                      .format(num_item_models_trained, len(item_ids_to_predict)))
    return nn_forecasts


def get_forecasts_for_nn(item_id, nn, values_used_to_predict, test_records):
    nn_forecasts = []

    for i in range(len(test_records)):
        test_record_being_predicted = test_records[i]
        predicted_quantity = nn.predict(values_used_to_predict)
        date = test_record_being_predicted.date

        percentage_error = error_calculations.percentage_error(test_record_being_predicted.quantity,
                                                               predicted_quantity)
        sales_qty = test_record_being_predicted.quantity
        nn_forecasts.append(PredictionRecord(item_id, date, sales_qty, predicted_quantity, percentage_error))

        # Add the newest predicted value to the list and remove the first one.
        # We continue by predicting using the already predicted values as truth
        values_used_to_predict.append(predicted_quantity)
        values_used_to_predict = values_used_to_predict[1:]

        # logging.debug("Predicted for item {item_id} for date {date}. Counter {counter}"
        #               .format(item_id=item_id, date=date, counter=i))
    return nn_forecasts
