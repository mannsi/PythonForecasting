import os
import forecast.IO.file_reader as file_reader
import forecast.graphs.quantitygraph as quantity_graph
import forecast.models.records as records
import forecast.data_manipulation.group as group
import forecast.statistics.error_calculations as error_calculations
import pickle
import logging


def init_logging():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def get_forecast_and_sales_records(group_by):
    """
    Gets the tuple grouped_sales_records, grouped_forecast_records
    :param group_by: string
    :return: ({item_id: list of records.ItemDateQuantityRecord}, {item_id: list of records..ItemDateQuantityRecord})
    """
    forecast_value_pickle_file = group_by + "forecast_values.pickle"
    sales_values_pickle_file = group_by + "sales_values.pickle"

    try:
        grouped_forecast_records = pickle.load(open(forecast_value_pickle_file, "rb"))
        logging.debug("Loading forecast list from memory")
    except (OSError, IOError) as e:
        forecast_file_abs_path = os.path.abspath(os.path.join("files", "forecast_values.txt"))
        forecast_records = file_reader.get_sample_forecast_values(forecast_file_abs_path)
        grouped_forecast_records = group_item_quantity_records(forecast_records, group_by)
        pickle.dump(grouped_forecast_records, open(forecast_value_pickle_file, "wb"))

        num_forecast_records = sum([len(item_records) for item_id, item_records in forecast_records.items()])
        logging.debug("Found {0} items with {1} number of forecast values and grouped them down to {2}"
                      .format(len(forecast_records), num_forecast_records, len(grouped_forecast_records)))

    try:
        grouped_sales_records = pickle.load(open(sales_values_pickle_file, "rb"))
        logging.debug("Loading sales list from memory")
    except (OSError, IOError) as e:
        sales_file_abs_path = os.path.abspath(os.path.join("files", "histories_sales.txt"))
        sales_records = file_reader.get_sample_history_sales_values(sales_file_abs_path)
        grouped_sales_records = group_item_quantity_records(sales_records, group_by)
        pickle.dump(grouped_sales_records, open(sales_values_pickle_file, "wb"))

        num_sales_records = sum([len(item_records) for item_id, item_records in sales_records.items()])
        logging.debug("Found {0} items with {1} number of sales values and grouped them down to {2}"
                      .format(len(sales_records), num_sales_records,len(grouped_sales_records)))

    return grouped_sales_records, grouped_forecast_records


def group_item_quantity_records(item_quantity_records, group_by):
    """

    :param item_quantity_records: {item_id: list of records.ItemDateQuantityRecord}
    :param group_by: string
    :return: {item_id: list of records.ItemDateQuantityRecord}
    """
    grouped_item_quantity_dict = {}
    for item_id, item_records in item_quantity_records.items():
        grouped_item_quantity_dict[item_id] = []
        dates = [x.date for x in item_records]
        quantities = [x.quantity for x in item_records]
        grouped_dates, grouped_quantities = group.by(dates, quantities, group_by)
        for i in range(len(grouped_dates)):
            date = grouped_dates[i]
            quantity = grouped_quantities[i]
            grouped_record = records.ItemDateQuantityRecord(item_id, date, quantity)
            grouped_item_quantity_dict[item_id].append(grouped_record)

    return grouped_item_quantity_dict


def join_sales_and_forecasts(sales_records, forecast_records):
    sale_and_predictions_pickle_file = "sale_and_predictions_list.p"
    try:
        sale_and_predictions_list = pickle.load(open(sale_and_predictions_pickle_file, "rb"))
        num_items = len(sale_and_predictions_list.distinct_item_ids())
        logging.debug("Number of joined sales and prediction records {0}".format(num_items))
        logging.debug("Loading joined sales and prediction list from memory")
    except (OSError, IOError) as e:
        logging.debug("Starting to create joined record list")
        sale_and_predictions_list = records.SaleAndPredictionRecordList(sales_records, forecast_records)
        logging.debug("Finished making the list")
        pickle.dump(sale_and_predictions_list, open(sale_and_predictions_pickle_file, "wb"))
    return sale_and_predictions_list


def show_graph(sale_and_predictions_list, item_id):
    sale_and_prediction_list_for_item = sale_and_predictions_list.records_list_for_item(item_id)
    sales_dates = [x.date for x in sale_and_prediction_list_for_item]
    sales_quantities = [x.sale_qty for x in sale_and_prediction_list_for_item]
    predicted_quantities = [x.predicted_qty for x in sale_and_prediction_list_for_item]

    graph = quantity_graph.QuantityGraph(
        sales_dates,
        [(sales_quantities, "Sales"), (predicted_quantities, "AGR forecast")],
        "Sales and predictions for item {0}".format(item_id))
    graph.display_graph()


def calculate_errors(sale_and_predictions_list: records.SaleAndPredictionRecordList):
    """
    Returns a list of tuples containing (item_id, float_mae_error, float_mape_error)
    :param sale_and_predictions_list:
    """
    error_list = []
    item_ids = sale_and_predictions_list.distinct_item_ids()
    for item_id in item_ids:
        records_for_item = sale_and_predictions_list.records_list_for_item(item_id)

        number_of_predictions = len([x for x in records_for_item if x.predicted_qty is not None])
        if number_of_predictions == 0:
            # Don't want to include none predicted items in statistics
            break

        mae_error = error_calculations.mae_error(records_for_item)
        # mape_error = error_calculations.mape_error(records_for_item)
        # error_list.append((item_id, mae_error, mape_error))
        error_list.append((item_id, mae_error))
    return error_list


def log_errors(error_list):
    """
    Log error values to current log output
    :param error_list: List[(str, float, float). List containing the tuples (item_id, float_mae_error, float_mape_error)
    """
    logging.debug("=ERROR LOGGING")

    logging.debug("Number of error items {0}".format(len(error_list)))

    # for error in error_list:
    #     logging.debug("{0} \t  {1} \t {2}".format(error[0], error[1], error[2]))

    average_abs_error = float(sum([x[1] for x in error_list])) / len(error_list)
    # average_percentage_error = float(sum([x[2] for x in error_list])) / len(error_list)

    logging.debug("Average abs forecast error: {0}".format(average_abs_error))
    # logging.debug("Average percentage forecast error: {0}".format(average_percentage_error))


def run():
    init_logging()
    sales_records, forecast_records = get_forecast_and_sales_records('W')
    logging.debug("Sales records: {0}, forecast records: {1}".format(len(sales_records), len(forecast_records)))
    sale_and_predictions_list = join_sales_and_forecasts(sales_records, forecast_records)
    error_list = calculate_errors(sale_and_predictions_list)
    log_errors(error_list)

    # TODO add my own forecast stuff and integrate with rest of the system

    # show_graph(sale_and_predictions_list, sale_and_predictions_list.first_item_id())


run()
