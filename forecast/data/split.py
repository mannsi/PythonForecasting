import datetime
from typing import List

from forecast.data.structures import ItemDateQuantityRecord
import forecast.data.verification as verification


def train_test_split(sales_prediction_records: List[ItemDateQuantityRecord], date_split: datetime):
    """
    Creates train_data, test_data
    :param sales_prediction_records:
    :param date_split: the date that splits training and test data
    :return: Tuple (List[ItemDateQuantityRecord], List[ItemDateQuantityRecord]) for train_data and test_data
    """

    train_data = [x for x in sales_prediction_records if x.date < date_split]
    test_data = [x for x in sales_prediction_records if date_split < x.date]

    verification.verify_training_records_are_sorted(train_data)  # Blows up if training records are not in date order

    return train_data, test_data

