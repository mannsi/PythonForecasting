import logging
from typing import List
from forecast.data_structures.records import ItemDateQuantityRecord
from forecast.data_structures.output import PredictionRecord
import forecast.models.verification.error_calculations as error_calculations


class MockModel:
    def __init__(self,
                 item_id: str,
                 sales_records: List[ItemDateQuantityRecord],
                 forecast_pro_forecast_records: List[ItemDateQuantityRecord],
                 number_of_predictions: int):
        # The AGR model is not really a model since I basically get the predicted values given
        self.number_of_predictions = number_of_predictions
        self.item_id = item_id
        self.predictions = self._create_forecasts(sales_records, forecast_pro_forecast_records)

    def test(self):
        """
        Calculates the errors from the sales_and_prediction_list
        :return: List[PredictionOutput]
        """
        if len(self.predictions) < self.number_of_predictions:
            raise Exception("Trying to make more predictions than there are records")

        return self.predictions

    def _create_forecasts(self, sales_records: List[ItemDateQuantityRecord],
                          prediction_records: List[ItemDateQuantityRecord])-> List[PredictionRecord]:
        output_list = []

        logging.debug("Starting to create joined record list")

        for sale_record in sales_records:
            for predicted_record in prediction_records:
                if predicted_record.date == sale_record.date:
                    predicted_qty = predicted_record.quantity
                    percentage_error = error_calculations.percentage_error(sale_record.quantity, predicted_qty)
                    output_list.append(
                        PredictionRecord(sale_record.item_id, sale_record.date,
                                         sale_record.quantity, predicted_qty, percentage_error))
                    break

        logging.debug("Finished making the list")
        return output_list
