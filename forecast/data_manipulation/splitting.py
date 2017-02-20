from typing import List, Dict
import datetime
from forecast.data_structures.records import ItemDateQuantityRecord, ItemDateRecord, SaleAndPredictionRecord


def to_train_and_test_date_split(sales_prediction_records: List[ItemDateQuantityRecord], date_split: datetime):
    """
    Creates train_data, test_data
    :param sales_prediction_records:
    :param date_split: the date that splits training and test data
    :return: Tuple (List[ItemDateQuantityRecord], List[ItemDateQuantityRecord]) for train_data and test_data
    """

    train_data = [x for x in sales_prediction_records if x.date < date_split]
    test_data = [x for x in sales_prediction_records if date_split < x.date]

    return train_data, test_data

