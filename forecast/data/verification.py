from typing import List
from forecast.data.structures import ItemDateQuantityRecord


def verify_training_records_are_sorted(training_records: List[ItemDateQuantityRecord]):
    is_sorted = _is_training_data_sorted(training_records)
    if not is_sorted:
        raise Exception("Training data for NN is not sorted by date !")


def _is_training_data_sorted(training_data: List[ItemDateQuantityRecord]):
    previous_date = None
    for training_record in training_data:
        if previous_date is None:
            previous_date = training_record.date
            continue

        if training_record.date < previous_date:
            return False

    return True