import datetime
from typing import List, Tuple

import forecast.graphs.quantity_graph as quantity_graph
from forecast.data.structures import ItemDateQuantityRecord, PredictionRecord


def show_quantity_graph(sales_values: List[ItemDateQuantityRecord],
                        prediction_lists: List[Tuple[str, List[PredictionRecord]]],
                        item_id):
    graph_line_list = []

    sales_dates = [x.date for x in sales_values]
    sales_quantities = [x.quantity for x in sales_values]
    graph_line_list.append((sales_quantities, "Sales"))

    for prediction_list in prediction_lists:
        prediction_name = prediction_list[0]
        predicted_records = prediction_list[1]
        generated_prediction_values = []
        for sales_value in sales_values:
            sale_date_found = False
            for predicted_record in predicted_records:
                if sales_value.date == predicted_record.date:
                    # This if for sanity checking
                    if sales_value.quantity != predicted_record.qty:
                        raise Exception("Why is the sales value and qty from prediction record not the same ?!?!?!?!")

                    generated_prediction_values.append(predicted_record.predicted_qty)
                    sale_date_found = True
            if not sale_date_found:
                generated_prediction_values.append(None)

        graph_line_list.append((generated_prediction_values, prediction_name))

    graph = quantity_graph.QuantityGraph(
        sales_dates,
        graph_line_list,
        "Sales and models for item {0}".format(item_id))
    graph.display_graph()

