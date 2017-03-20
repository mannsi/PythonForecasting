import forecast.models.verification.error_calculations as error_calculations
from forecast.data.structures import PredictionRecord


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
