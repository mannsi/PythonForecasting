class ItemDateRecord:
    def __init__(self,item_id, date):
        self.date = date
        self.item_id = item_id


class ItemDateQuantityRecord:
    def __init__(self, item_id, date, quantity):
        self.quantity = quantity
        self.date = date
        self.item_id = item_id
