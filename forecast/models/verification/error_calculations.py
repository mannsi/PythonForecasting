import math
import logging
from typing import Dict, List

from forecast.data_structures.output import PredictionRecord


def average_percentage_error(predictions: Dict[str, List[PredictionRecord]],
                             dates_to_measure_error: List[int]) -> List[int]:
    max_num_predictions_needed = max(dates_to_measure_error)
    date_measured_errors = []

    sales_and_prediction_sums_per_item = {}  # Dict for items and contains a tuple
    for item_id in predictions.keys():
        sales_and_prediction_sums_per_item[item_id] = (0, 0)

    for date_index in range(max_num_predictions_needed):
        predictions_for_date = [x[date_index] for x in predictions.values()]
        unique_prediction_dates = len(set([x.date for x in predictions_for_date]))
        if unique_prediction_dates != 1:
            raise Exception("All predictions should be for the same date. Something is wrong with the data")

        for prediction_for_date in predictions_for_date:
            item_id = prediction_for_date.item_id
            sale_sum_for_item, prediction_sum_for_item_ = sales_and_prediction_sums_per_item[item_id]
            sale_sum_for_item += prediction_for_date.qty
            prediction_sum_for_item_ += prediction_for_date.predicted_qty
            sales_and_prediction_sums_per_item[item_id] = (sale_sum_for_item, prediction_sum_for_item_)

        if date_index + 1 in dates_to_measure_error:
            # First get percentage errors for every item
            list_of_item_errors = []
            for item_id, (item_sale_sum, item_prediction_sum) in sales_and_prediction_sums_per_item.items():
                current_percentage_error_for_item = percentage_error(item_sale_sum, item_prediction_sum)
                list_of_item_errors.append(current_percentage_error_for_item)

            # The official error is the average of each items error
            average_error = float(sum(list_of_item_errors)) / len(list_of_item_errors)
            date_measured_errors.append(average_error)

    return date_measured_errors


def percentage_error(value, predicted_value):
    if value == 0:
        return None
    return float(100 * math.fabs(value-predicted_value)) / value
