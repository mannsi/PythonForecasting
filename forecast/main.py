import os
import forecast.IO.file_reader as file_reader
import forecast.graphs.quantity_graph as quantity_graph

forecast_file_abs_path = os.path.abspath(os.path.join("files", "forecast_values.txt"))
forecast_values = file_reader.get_sample_forecast_values(forecast_file_abs_path)

sales_file_abs_path = os.path.abspath(os.path.join("files", "histories_sales.txt"))
sales_values = file_reader.get_sample_history_sales_values(sales_file_abs_path)


print("Found {0} number of forecast values".format(len(forecast_values)))
print("Found {0} number of forecast values".format(len(sales_values)))

graph = quantity_graph.Quantity_graph(sales_values,forecast_values)
graph.display_graph()