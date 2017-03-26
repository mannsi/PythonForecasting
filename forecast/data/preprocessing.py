from typing import List


def moving_average(training_data: List[int], testing_data: List[int]):
    """
    Takes training data and testing data and creates moving average values of window size 3 for training records while
    not doing anything to the testing_data
    :param training_data:
    :param testing_data:
    :return:
    """

    moving_average_training_data = []

    for i in range(len(training_data)):
        if i == 0:
            # First record is special because there is no record before it
            average_value = float(training_data[0] + training_data[1]) / 2
        elif i == len(training_data) - 1:
            # Last value is also special because there is no value behind it
            average_value = float(training_data[i-1] + training_data[i]) / 2
        else:
            # Take average value of item i and the values before and after
            average_value = float(training_data[i-1] + training_data[i] + training_data[i+1]) / 3
        moving_average_training_data.append(average_value)

    return moving_average_training_data, testing_data


def diff(training_data: List[int], testing_data: List[int]):
    """
    Creates diff series for training data. Test data is kept as is
    :param training_data:
    :param testing_data:
    :return:
    """

    diff_training_data = []

    for i in range(len(training_data) - 1):
        diff_value = training_data[i+1]-training_data[i]
        diff_training_data.append(diff_value)

    return diff_training_data, testing_data
