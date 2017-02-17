from typing import List
from forecast.data_structures.records import SaleAndPredictionRecord
import forecast.models.verification.error_calculations as error_calculations


class MockModel:
    def __init__(self, item_id, sales_and_prediction_list: List[SaleAndPredictionRecord]):
        # The AGR model is not really a model since I basically get the predicted value from files
        self.item_id = item_id
        self.sales_and_prediction_list = sales_and_prediction_list

    def test(self):
        """
        Calculates the errors from the sales_and_prediction_list
        :return: Tuple (float_mae_error, float_mape_error)
        """
        mae_error = error_calculations.mae(self.sales_and_prediction_list)
        mape_error = error_calculations.mape(self.sales_and_prediction_list)
        return mae_error, mape_error