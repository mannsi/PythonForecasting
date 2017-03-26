import forecast.models.verification.error_calculations as error_calculations
from forecast.data.structures import PredictionRecord


def get_forecasts_for_nn(item_id, nn, values_used_to_predict, test_data):
    nn_forecasts = []

    for i in range(len(test_data)):
        true_value = test_data[i]
        predicted_quantity = nn.predict(values_used_to_predict)

        percentage_error = error_calculations.percentage_error(true_value,
                                                               predicted_quantity)
        nn_forecasts.append(PredictionRecord(item_id, '', true_value, predicted_quantity, percentage_error))

        # Add the newest predicted value to the list and remove the first one.
        # We continue by predicting using the already predicted values as truth
        values_used_to_predict.append(predicted_quantity)
        values_used_to_predict = values_used_to_predict[1:]

        # logging.debug("Predicted for item {item_id} for date {date}. Counter {counter}"
        #               .format(item_id=item_id, date=date, counter=i))
    return nn_forecasts


def get_forecasts_for_nn_with_diff(item_id, nn, values_used_to_predict, last_training_value, test_data):
    """
    The difference between this method and get_forecasts_for_nn is that values_used_to_predict are diff values
    and the last_training_value is used with predictions to get an actual quantity value
    :param item_id:
    :param nn:
    :param values_used_to_predict:
    :param test_data:
    :return:
    """
    nn_forecasts = []
    previous_predicted_qty = last_training_value

    for i in range(len(test_data)):
        true_value = test_data[i]
        predicted_diff_quantity = nn.predict(values_used_to_predict)
        predicted_quantity = previous_predicted_qty + predicted_diff_quantity

        percentage_error = error_calculations.percentage_error(true_value,
                                                               predicted_quantity)
        nn_forecasts.append(PredictionRecord(item_id, '', true_value, predicted_quantity, percentage_error))

        # Add the newest predicted value to the list and remove the first one.
        # We continue by predicting using the already predicted values as truth
        values_used_to_predict.append(predicted_quantity)
        values_used_to_predict = values_used_to_predict[1:]
        previous_predicted_qty = predicted_quantity

        # logging.debug("Predicted for item {item_id} for date {date}. Counter {counter}"
        #               .format(item_id=item_id, date=date, counter=i))
    return nn_forecasts
