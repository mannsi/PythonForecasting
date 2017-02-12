import os
import forecast.IO.file_reader as file_reader
import forecast.graphs.quantitygraph as quantity_graph
import forecast.models.records as records
import pickle
import logging


def init_logging():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def get_forecast_and_sales_records():
    forecast_value_pickle_file = "forecast_values.p"
    sales_values_pickle_file = "sales_values.p"

    try:
        forecast_records = pickle.load(open(forecast_value_pickle_file, "rb"))
    except (OSError, IOError) as e:
        forecast_file_abs_path = os.path.abspath(os.path.join("files", "forecast_values.txt"))
        forecast_records = file_reader.get_sample_forecast_values(forecast_file_abs_path)
        pickle.dump(forecast_records, open(forecast_value_pickle_file, "wb"))

    try:
        sales_records = pickle.load(open(sales_values_pickle_file, "rb"))
    except (OSError, IOError) as e:
        sales_file_abs_path = os.path.abspath(os.path.join("files", "histories_sales.txt"))
        sales_records = file_reader.get_sample_history_sales_values(sales_file_abs_path)
        pickle.dump(forecast_records, open(sales_values_pickle_file, "wb"))

    logging.debug("Found {0} number of forecast values".format(len(forecast_records)))
    logging.debug("Found {0} number of forecast values".format(len(sales_records)))

    return sales_records, forecast_records


def get_sales_and_predictions_list():
    sale_and_predictions_pickle_file = "sale_and_predictions_list.p"
    try:
        sale_and_predictions_list = pickle.load(open(sale_and_predictions_pickle_file, "rb"))
    except (OSError, IOError) as e:
        sales_records, forecast_records = get_forecast_and_sales_records()
        logging.debug("Starting to create joined record list")
        sale_and_predictions_list = records.SaleAndPredictionRecordList(sales_records, forecast_records)
        logging.debug("Finished making the list")
        pickle.dump(sale_and_predictions_list, open(sale_and_predictions_pickle_file, "wb"))
    return sale_and_predictions_list


def show_graph(sale_and_predictions_list, item_id):
    graph = quantity_graph.QuantityGraph(sale_and_predictions_list, 'M')
    graph.display_graph(item_id)


def run():
    init_logging()
    sale_and_predictions_list = get_sales_and_predictions_list()
    show_graph(sale_and_predictions_list, sale_and_predictions_list.first_item_id())

run()