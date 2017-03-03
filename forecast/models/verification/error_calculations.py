import math
from typing import Dict, List

from forecast.data.structures import PredictionRecord


def weighted_average(errors: List[float]) -> float:

    """
    Takes a list of error values and applies the weighting before calculating average

    The weighting gives more weight to the first items and less to the last ones (linearly)

    :param errors: list of error values
    """
    total_number_of_errors = len(errors)
    weight_sum = sum([x + 1 for x in range(len(errors))])  # Sum over the number of errors. 3 errors would result in 1+2+3=6 weight sum
    average_error_sum = 0

    for i in range(len(errors)):
        error = errors[i]
        average_error_sum += error * float(total_number_of_errors - i) / weight_sum

    return average_error_sum


def average_percentage_error(predictions: Dict[str, List[PredictionRecord]],
                             num_prediction_per_item: int) -> List[float]:
    all_item_ids = predictions.keys()
    average_errors_per_prediction_date = []

    for date_index in range(num_prediction_per_item):
        predictions_for_date = [x[date_index] for x in predictions.values()]
        unique_prediction_dates = len(set([x.date for x in predictions_for_date]))
        if unique_prediction_dates != 1:
            raise Exception("All predictions should be for the same date. Something is wrong with the data")

        # Get sale and prediction sums for each item
        sales_and_prediction_sums_per_item = {}
        for item_id in all_item_ids:
            item_predictions_for_date = [x for x in predictions_for_date if x.item_id == item_id]
            sales_sum_for_item_for_date = sum([x.qty for x in item_predictions_for_date])
            predicted_sum_for_item_for_date = sum([x.predicted_qty for x in item_predictions_for_date])
            sales_and_prediction_sums_per_item[item_id] = (sales_sum_for_item_for_date, predicted_sum_for_item_for_date)

        # Calculate the average percentage error for date over all items
        # First get percentage errors for every item
        list_of_item_errors = []
        for item_id, (item_sale_sum, item_prediction_sum) in sales_and_prediction_sums_per_item.items():
            current_percentage_error_for_item = percentage_error(item_sale_sum, item_prediction_sum)
            list_of_item_errors.append(current_percentage_error_for_item)

        # The official error is the average of each items error
        average_error = float(sum(list_of_item_errors)) / len(list_of_item_errors)
        average_errors_per_prediction_date.append(average_error)

    return average_errors_per_prediction_date


def percentage_error(value, predicted_value):
    if value == 0:
        return None
    return float(100 * math.fabs(value-predicted_value)) / value
