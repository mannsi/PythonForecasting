class Quantity_graph:
    def __init__(self,real_sales, predictions):
        self.real_sales=real_sales
        self.predictions=predictions

    def display_graph(self):
        import matplotlib.pyplot as plt
        plt.plot([1, 2, 3, 4], [1, 4, 9, 16], 'ro')
        #plt.axis([0, 6, 0, 20])
        plt.show()
