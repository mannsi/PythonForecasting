import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import forecast.data_manipulation.group as group

class QuantityGraph:
    def __init__(self, sale_and_predictions_list, period):
        """
        :param sale_and_predictions_list: SaleAndPredictionRecordList
        :param period: How to group the data into periods for the graph. 'D' for days, 'W' for weeks, 'M' for months
        """
        self.period = period
        self.sale_and_predictions_list = sale_and_predictions_list

    def display_graph(self, item_id):
        # Get the data
        sale_and_prediction_list_for_item = self.sale_and_predictions_list.sale_and_prediction_list_for_item(item_id)
        sales_dates = [x.date for x in sale_and_prediction_list_for_item]
        sales_quantities = [x.sale_qty for x in sale_and_prediction_list_for_item]
        predicted_quantities = [x.predicted_qty for x in sale_and_prediction_list_for_item]

        if self.period == 'D':
            time_axis = sales_dates
            sales_values = sales_quantities
            prediction_values = predicted_quantities
        elif self.period == 'W':
            time_axis, sales_values = group.by_week_sums(sales_dates, sales_quantities)
            time_axis, prediction_values = group.by_week_sums(sales_dates, predicted_quantities)
        elif self.period == 'M':
            time_axis, sales_values = group.by_month_sums(sales_dates, sales_quantities)
            time_axis, prediction_values = group.by_month_sums(sales_dates, predicted_quantities)

        fig, ax = plt.subplots(1)
        fig.autofmt_xdate()

        plt.plot(time_axis, sales_values, label="Real", marker='o')
        plt.plot(time_axis, prediction_values, label="AGR predict", marker='o')
        plt.legend(bbox_to_anchor=(0.8, 1), loc=2, borderaxespad=0.)

        xfmt = mdates.DateFormatter('%d-%m-%y')
        ax.xaxis.set_major_formatter(xfmt)
        plt.show()

