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


class SaleAndPredictionRecordList:
    def __init__(self, sales_record_dict, prediction_record_dict):
        """
        :param sales_record_dict:  list of ItemDateQuantityRecord
        :param prediction_record_dict: list of ItemDateQuantityRecord
        """
        self.sale_and_predictions_list = []

        for sale_record_id, sale_record in sales_record_dict.items():
            predicted_qty = None  # default if no prediction exists for sale

            if sale_record_id in prediction_record_dict:
                predicted_record = prediction_record_dict[sale_record_id]
                predicted_qty = predicted_record.quantity

            self.sale_and_predictions_list.append(
                SaleAndPredictionRecord(sale_record.item_id, sale_record.date, sale_record.quantity, predicted_qty))

    def sale_and_prediction_list_for_item(self, item_id):
        """

        :param item_id:
        :return: list of SaleAndPredictionRecord
        """
        records_for_item = [x for x in self.sale_and_predictions_list if x.item_id == item_id]
        records_for_item.sort(key=lambda record: record.date)
        return records_for_item

    def first_item_id(self):
        return self.sale_and_predictions_list[0].item_id
