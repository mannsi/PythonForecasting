from typing import List


class AbstractModel:
    def train(self, training_data: List[float]) -> float:
        pass

    def predict(self, last_years_data: List[float]) -> float:
        return 0
