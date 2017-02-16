from typing import List
import logging
from forecast.data_structures.records import SaleAndPredictionRecord
import forecast.models.verification.error_calculations as error_calculations

class MockModel:
    def __init__(self, sales_and_prediction_list: List[SaleAndPredictionRecord]):
        # TODO each model should only include data on one item
        # The AGR model is not really a model since I basically get the predicted value from files
        self.sales_and_prediction_list = sales_and_prediction_list

    def test(self):
        """
        Calculates the errors from the initial sales_and_prediction_list
        :return: List of tuples (item_id, float_mae_error, float_mape_error)
        """
        error_list = []
        item_ids = self.sales_and_prediction_list.distinct_item_ids()
        logging.debug("Number of unique item ids found when calculating errors: {0}".format(len(item_ids)))
        for item_id in item_ids:
            records_for_item = self.sales_and_prediction_list.records_list_for_item(item_id)


            # TODO move this functionality to data cleaning
            number_of_predictions = len([x for x in records_for_item if x.predicted_qty is not None])
            if number_of_predictions == 0:
                # Don't want to include none predicted items in statistics
                logging.debug("No models for item with id {0}".format(item_id))
                continue

            mae_error = error_calculations.mae(records_for_item)
            mape_error = error_calculations.mape(records_for_item)
            error_list.append((item_id, mae_error, mape_error))
        return error_list