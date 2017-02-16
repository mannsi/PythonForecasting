import math
import logging
from typing import List


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


