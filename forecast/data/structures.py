class PredictionRecord:
    def __init__(self, item_id, date, qty, predicted_qty, error):
        self.date = date
        self.qty = qty
        self.predicted_qty = predicted_qty
        self.error = error
        self.item_id = item_id


class ItemDateRecord:
    def __init__(self,item_id, date):
        self.date = date
        self.item_id = item_id


class ItemDateQuantityRecord:
    def __init__(self, item_id, date, quantity):
        self.quantity = quantity
        self.date = date
        self.item_id = item_id