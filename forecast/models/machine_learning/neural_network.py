from typing import List
from forecast.data_structures.records import SaleAndPredictionRecord,ItemDateRecord


class NeuralNetwork:
    def __init__(self):
        # TODO set parameters here
        pass

    def train(self, training_data: List[SaleAndPredictionRecord]):
        pass

    def predict(self, item_to_predict_quantity:ItemDateRecord) -> float:
        return 0
