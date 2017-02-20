from typing import List
from forecast.data_structures.records import ItemDateQuantityRecord


class AbstractModel:
    def train(self, training_data: List[float]) -> float:
        pass

    def predict(self, last_years_data: List[float]) -> float:
        return 0
