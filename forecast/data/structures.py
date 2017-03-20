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


class ItemForecastResult:
    def __init__(self, item_id, hidden_nodes, input_nodes, hidden_layers, training_error, weighted_error, errors_per_month):
        self.item_id = item_id
        self.hidden_nodes = hidden_nodes
        self.input_nodes = input_nodes
        self.hidden_layers = hidden_layers
        self.training_error = training_error
        self.weighted_error = weighted_error
        self.errors_per_month = errors_per_month
