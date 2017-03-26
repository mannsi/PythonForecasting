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
