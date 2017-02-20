from typing import List
from forecast.data_structures.records import SaleAndPredictionRecord
from forecast.data_structures.output import PredictionOutput
import forecast.models.verification.error_calculations as error_calculations


class MockModel:
    def __init__(self, item_id, sales_and_prediction_list: List[SaleAndPredictionRecord], number_of_predictions:int):
        # The AGR model is not really a model since I basically get the predicted value from files
        self.number_of_predictions = number_of_predictions
        self.item_id = item_id
        sales_and_prediction_list.sort(key=lambda record: record.date)
        self.sales_and_prediction_list = sales_and_prediction_list

    def test(self):
        """
        Calculates the errors from the sales_and_prediction_list
        :return: List[PredictionOutput]
        """
        if len(self.sales_and_prediction_list) < self.number_of_predictions:
            raise Exception("Trying to make more predictions than there are records")

        output_list = []

        for i in range(self.number_of_predictions):
            sale_and_prediction_record = self.sales_and_prediction_list[i]
            date = sale_and_prediction_record.date
            sale_qty = sale_and_prediction_record.sale_qty
            predicted_qty = sale_and_prediction_record.predicted_qty
            percentage_error = error_calculations.percentage_error(sale_qty, predicted_qty)
            output_list.append(PredictionOutput(self.item_id, date, sale_qty, predicted_qty, percentage_error))

        return output_list
