from typing import List
from forecast.models.abstract_model import AbstractModel
from forecast.data_structures.records import ItemDateRecord, SaleAndPredictionRecord
import forecast.models.verification.error_calculations as error_calculations


def accuracy(model: AbstractModel, test_data: List[ItemDateRecord], test_data_results: List[float]) -> (float, float, List[SaleAndPredictionRecord]):
    """
    Calculates the mean absolute error and mean absolute percentage error for the given model and test data

    :param model: The model to measure
    :param test_data: The data to test on
    :param test_data_results: The true test data results
    :return: Tuple of (mae, mape, list_of_sale_prediction_records)
    """
    sale_and_prediction_records = []
    for i in range(len(test_data)):
        test_data_record = test_data[i]
        predicted_value = model.predict(test_data_record)
        actual_value = test_data_results[i]
        sale_and_prediction_records.append(
            SaleAndPredictionRecord(test_data_record.item_id, test_data_record.date, actual_value, predicted_value))

    mean_absolute_error = error_calculations.mae(sale_and_prediction_records)
    mean_absolute_percentage_error = error_calculations.mape(sale_and_prediction_records)

    return mean_absolute_error, mean_absolute_percentage_error, sale_and_prediction_records
