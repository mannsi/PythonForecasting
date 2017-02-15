import math
import logging


class ItemDateQuantityRecord:
    def __init__(self, item_id, date, quantity):
        self.quantity = quantity
        self.date = date
        self.item_id = item_id

    def id(self):
        return self.item_id + str(self.date)


class SaleAndPredictionRecord:
    def __init__(self, item_id, date, sale_qty, predicted_qty):
        self.item_id = item_id
        self.date = date
        self.sale_qty = sale_qty
        self.predicted_qty = predicted_qty

    def abs_error(self):
        return math.fabs(self.sale_qty - self.predicted_qty)


class SaleAndPredictionRecordList:
    def __init__(self, sales_record_dict, prediction_record_dict):
        """
        :param sales_record_dict:  {item_id: list of ItemDateQuantityRecord}
        :param prediction_record_dict: {item_id: list of ItemDateQuantityRecord}
        """
        self.sale_and_predictions_list = []

        for item_id, sale_records_for_item in sales_record_dict.items():
            predicted_records_for_item = prediction_record_dict[item_id]

            for sale_record in sale_records_for_item:
                if math.isnan(sale_record.quantity):
                    logging.error("Sales amount is Nan. Item {0}, date {1}".format(item_id, sale_record.date))
                    break;
                predicted_qty = None
                for predicted_record in predicted_records_for_item:
                    if predicted_record.date == sale_record.date:
                        predicted_qty = predicted_record.quantity
                        break
                self.sale_and_predictions_list.append(SaleAndPredictionRecord(sale_record.item_id, sale_record.date, sale_record.quantity, predicted_qty))

    def records_list_for_item(self, item_id):
        """

        :param item_id: string
        :return: list of SaleAndPredictionRecord
        """
        records_for_item = [x for x in self.sale_and_predictions_list if x.item_id == item_id]
        # records_for_item.sort(key=lambda record: record.date)
        return records_for_item

    def update_records_for_item(self, item_id, records):
        """
        Update the sale and prediction records for an item

        :param item_id: string
        :param records: list of SaleAndPredictionRecord
        """
        # Remove old values for item
        self.sale_and_predictions_list = [x for x in self.sale_and_predictions_list if x.item_id != item_id]

        # Add the new item records
        self.sale_and_predictions_list.extend(records)

    def first_item_id(self):
        return self.sale_and_predictions_list[0].item_id

    def distinct_item_ids(self):
        all_item_ids = list(set([x.item_id for x in self.sale_and_predictions_list]))
        return all_item_ids
