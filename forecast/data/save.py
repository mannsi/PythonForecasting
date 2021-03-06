import logging
from typing import Dict, List

import forecast.models.verification.error_calculations as error_calculations
from forecast.data.structures import PredictionRecord


def save_prediction_results(predictions: List[Dict[str, List[PredictionRecord]]],
                            model_name: str, num_prediction_per_item: int):
    """
    Log error values to current log output
    :param num_prediction_per_item: number of predictions per item
    :param model_name: the name of the model being used
    :param predictions:
    """

    average_weighted_errors = []
    for prediction in predictions:
        error_list = error_calculations.average_percentage_error(prediction, num_prediction_per_item)
        average_weighted_error_for_prediction = error_calculations.weighted_average(error_list)
        average_weighted_errors.append(average_weighted_error_for_prediction)

    average_weighted_error = float(sum(average_weighted_errors)) / len(average_weighted_errors)
    logging.warning("Average weighted errors for '{model_name}' {average_weighted_error:.2f}"
                    .format(model_name=model_name, average_weighted_error=average_weighted_error))

    for i in range(len(error_list)):
        error = error_list[i]
        logging.info("=Average percentage error for period {period}: {error_val:.2f}% using model {model}"
                     .format(period=i+1, error_val=error, model=model_name))


