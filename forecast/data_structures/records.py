import math


class ItemDateRecord:
    def __init__(self,item_id, date):
        self.date = date
        self.item_id = item_id


class ItemDateQuantityRecord:
    def __init__(self, item_id, date, quantity):
        self.quantity = quantity
        self.date = date
        self.item_id = item_id


class SaleAndPredictionRecord:
    def __init__(self, item_id, date, sale_qty, predicted_qty):
        self.item_id = item_id
        self.date = date
        self.sale_qty = sale_qty
        self.predicted_qty = predicted_qty

