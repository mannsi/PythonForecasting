from typing import List
from forecast.data_structures.records import SaleAndPredictionRecord, ItemDateRecord


class AbstractModel:
    def train(self, training_data: List[SaleAndPredictionRecord]):
        pass

    def predict(self, last_years_data) -> float:
        return 0
