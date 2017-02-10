import os
import forecast.IO.file_reader as file_reader
import forecast.graphs.quantity_graph as quantity_graph
import pickle

forecast_value_pickle_file = "forecast_values.p"
sales_values_pickle_file = "sales_values.p"

try:
    forecast_values = pickle.load(open(forecast_value_pickle_file, "rb"))
except (OSError, IOError) as e:
    forecast_file_abs_path = os.path.abspath(os.path.join("files", "forecast_values.txt"))
    forecast_values = file_reader.get_sample_forecast_values(forecast_file_abs_path)
    pickle.dump(forecast_values, open(forecast_value_pickle_file, "wb"))

try:
    sales_values = pickle.load(open(sales_values_pickle_file, "rb"))
except (OSError, IOError) as e:
    sales_file_abs_path = os.path.abspath(os.path.join("files", "histories_sales.txt"))
    sales_values = file_reader.get_sample_history_sales_values(sales_file_abs_path)
    pickle.dump(forecast_values, open(sales_values_pickle_file, "wb"))


print("Found {0} number of forecast values".format(len(forecast_values)))
print("Found {0} number of forecast values".format(len(sales_values)))


graph = quantity_graph.Quantity_graph(sales_values,forecast_values)
graph.display_graph()