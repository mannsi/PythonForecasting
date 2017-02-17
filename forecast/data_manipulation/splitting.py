from typing import List, Dict
import datetime
from forecast.data_structures.records import ItemDateQuantityRecord, ItemDateRecord, SaleAndPredictionRecord


def to_train_and_test_date_split(sales_prediction_records: List[ItemDateQuantityRecord], date_split: datetime):
    """
    Creates training data, test data and test data answers from a sales prediction dataset
    :param sales_prediction_records:
    :param date_split: the date that splits training and test data
    :return: Tuple (training_data: List[SaleAndPredictionRecord], test_data: List[ItemDateRecord], test_data_answers:List[float])
    """

    training_data = [x for x in sales_prediction_records if x.date < date_split]
    uncleaned_test_data_list = [x for x in sales_prediction_records if date_split < x.date]
    test_data = []
    test_data_answers = []

    for uncleaned_test_data in uncleaned_test_data_list:
        test_data.append(ItemDateRecord(uncleaned_test_data.item_id, uncleaned_test_data.date))
        test_data_answers.append(uncleaned_test_data.quantity)

    return training_data, test_data, test_data_answers

