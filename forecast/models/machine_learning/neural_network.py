import numpy
import math
from typing import List
from forecast.models.abstract_model import AbstractModel
from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import EarlyStopping
from keras import backend as K
from keras import optimizers


class NeuralNetwork(AbstractModel):
    def __init__(self, num_hidden_layers: int, num_nodes_per_hidden_layer: int, num_input_nodes: int):
        """

        :param data_periods:
        """
        self.neural_network_model = Sequential()
        self.num_nodes_per_hidden_layer = num_nodes_per_hidden_layer
        self.num_hidden_layers = num_hidden_layers
        self.num_input_nodes = num_input_nodes

    def train(self, training_data: List[float]):
        K.clear_session()
        if len(training_data) < self.num_input_nodes:
            raise Exception("Not enough training data records to train. Need {need} but got {got}"
                            .format(need=self.num_input_nodes, got=len(training_data)))

        train_x, train_y = self._create_training_dataset(training_data, self.num_input_nodes)

        # create and fit MLP neural_network_model

        for i in range(self.num_hidden_layers):
            self.neural_network_model.add(
                Dense(self.num_nodes_per_hidden_layer, input_dim=self.num_input_nodes, activation='relu'))
        self.neural_network_model.add(Dense(1))

        sgd = optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
        self.neural_network_model.compile(loss='mean_squared_error', optimizer=sgd)
        # early_stopping = EarlyStopping(monitor='val_loss', patience=20, verbose=2, mode='auto')
        # self.neural_network_model.fit(train_x, train_y, nb_epoch=500, batch_size=1, verbose=0, validation_split=0.1, callbacks=[early_stopping])


        self.neural_network_model.fit(train_x, train_y, nb_epoch=500, batch_size=10, verbose=0)

        train_score = self.neural_network_model.evaluate(train_x, train_y, verbose=0)
        return math.sqrt(train_score)  # The train score is the mean squared error. Need to sqrt it to get the actual error.

    def predict(self, last_years_data: List[float]) -> float:
        if self.num_input_nodes != len(last_years_data):
            raise Exception("Expected {ex_num_values} number of values while predicting".format(ex_num_values=self.num_input_nodes))

        prediction_input = numpy.array([last_years_data])
        predicted_array = self.neural_network_model.predict(prediction_input)
        return predicted_array[0][0]

    def _create_training_dataset(self, dataset, look_back):
        dataX, dataY = [], []
        for i in range(len(dataset) - look_back - 1):
            a = dataset[i:(i + look_back)]
            dataX.append(a)
            dataY.append(dataset[i + look_back])
        return numpy.array(dataX), numpy.array(dataY)


class NeuralNetworkConfig:
    def __init__(self,
                 description,
                 num_hidden_layers,
                 num_hidden_nodes_per_layer,
                 num_input_nodes):
        self.description = description
        self.num_hidden_layers = num_hidden_layers
        self.num_hidden_nodes_per_layer = num_hidden_nodes_per_layer
        self.num_input_nodes = num_input_nodes
