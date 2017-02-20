

class PredictionOutput:
    def __init__(self, item_id, date, qty, predicted_qty, error):
        self.date = date
        self.qty = qty
        self.predicted_qty = predicted_qty
        self.error = error
        self.item_id = item_id

