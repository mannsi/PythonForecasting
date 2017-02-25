import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class QuantityGraph:
    def __init__(self, x_values, y_values_list, title):
        """

        :param x_values:  list of date values
        :param y_values_list:  list of tuples of (y_float_values, y_legend)
        :param title: string
        """
        self.title = title
        self.y_values_list = y_values_list
        self.x_values = x_values

    def display_graph(self):
        fig, ax = plt.subplots(1)
        fig.suptitle(self.title)
        # fig.autofmt_xdate()

        for values, label in self.y_values_list:
            plt.plot(self.x_values, values, label=label, marker='o')
        plt.legend(bbox_to_anchor=(0.5, 1), loc=2, borderaxespad=0.)
        plt.legend()

        # xfmt = mdates.DateFormatter('%d-%m-%y')
        # ax.xaxis.set_major_formatter(xfmt)

        axes = plt.gca()
        axes.set_ylim(ymin=0)

        years = mdates.YearLocator()  # every year
        months = mdates.MonthLocator()  # every month
        yearsFmt = mdates.DateFormatter('%Y')

        # format the ticks
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(yearsFmt)
        ax.xaxis.set_minor_locator(months)

        ax.grid(True)

        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()

        manager = plt.get_current_fig_manager()
        manager.window.state('zoomed')  # works fine on Windows!
        # manager.resize(*manager.window.maxsize()) # Maybe this works on linux


        plt.show()

