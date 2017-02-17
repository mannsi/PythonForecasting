from typing import List
from forecast.data_structures.records import ItemDateQuantityRecord,ItemDateRecord


class NeuralNetwork:
    def __init__(self, item_id, data_periods:str):
        """

        :param item_id:
        :param data_periods:
        """
        # TODO create the NN
        # self.nn =
        self.item_id = item_id
        if data_periods == 'W':
            self.number_of_data_lag_values = 52
        elif data_periods == 'M':
            self.number_of_data_lag_values = 12

    def train(self, training_data: List[ItemDateQuantityRecord]):
        data_is_sorted = self._is_training_data_sorted(training_data)
        if not data_is_sorted:
            raise Exception("Training data for NN is not sorted by date !")

        training_tuples = self._get_training_tuples(training_data)

        for nn_input_values, nn_output_answer in training_tuples:
            # TODO create and train the NN
            pass

    def predict(self, last_years_data: List[ItemDateQuantityRecord]) -> float:
        if self.number_of_data_lag_values != len(last_years_data):
            raise Exception("Expected {ex_num_values} number of values while predicting".format(ex_num_values = self.number_of_data_lag_value)

        # TODO create prediction using model

        return 100

    def _is_training_data_sorted(self, training_data):
        previous_date = None
        for training_record in training_data:
            if previous_date is None:
                previous_date = training_record.date
                continue

            if training_record.date < previous_date:
                return False

        return True

    def _get_training_tuples(self, training_data: List[ItemDateQuantityRecord]) -> List[(List,float)]:
        """
        Takes all the training data and creates a list of tuples. Each tuple contains one training batch and
        the correct answer to that batch
        """
        training_tuples_list = []
        num_tuples = len(training_data) - self.number_of_data_lag_values - 1  # Can't use the last value since there is no ground truth there

        if num_tuples < 1:
            raise Exception("Too few training values to train. Only {0} values provided".format(len(training_data)))

        for i in range(num_tuples):
            training_records = training_data[i:i+self.number_of_data_lag_values]
            correct_answer = training_data[i+self.number_of_data_lag_values + 1]
            training_tuples_list.append((training_records, correct_answer))
