import forecast.data_structures.records as records
from typing import List


def mae(list_of_sale_and_prediction_records: List[records.SaleAndPredictionRecord]):
    """
    Gets the mean absolute error from the list of records

    :param list_of_sale_and_prediction_records: list of SaleAndPredictionRecord
    :return: float with the mae error
    """
    # Filter out values where there is no prediction
    filtered_records = [x for x in list_of_sale_and_prediction_records if x.predicted_qty is not None]
    all_abs_errors = [x.abs_error() for x in filtered_records]
    abs_error_sum = sum(all_abs_errors)
    mae = float(abs_error_sum) / len(filtered_records)
    return mae


def mape(list_of_sale_and_prediction_records: List[records.SaleAndPredictionRecord]):
    """
    Gets the mean absolute percentage error from the list of records

    :param list_of_sale_and_prediction_records: list of SaleAndPredictionRecord
    :return: float with the mae error
    """
    # Filter out values where there is no prediction
    filtered_records = [x for x in list_of_sale_and_prediction_records if x.predicted_qty is not None and x.sale_qty != 0]
    all_percentage_errors = [float(100 * x.abs_error())/x.sale_qty for x in filtered_records]
    percentage_error_sum = sum(all_percentage_errors)
    mae = float(percentage_error_sum) / len(filtered_records)
    return mae


def percentage_error(record:records.SaleAndPredictionRecord):
    if record.sale_qty == 0:
        return None

    return float(100 * record.abs_error())/record.sale_qty
