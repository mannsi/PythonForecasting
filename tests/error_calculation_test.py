# import unittest
#
# import forecast.models.verification.error_calculations as error_calculations
# from forecast.data_structures.records import SaleAndPredictionRecord
#
#
# class ErrorCalculation(unittest.TestCase):
#
#     def test_basic(self):
#         data = []
#         data.append(SaleAndPredictionRecord('itemid', 'date', 1, 2))  # 1 error, 100% error
#         data.append(SaleAndPredictionRecord('itemid', 'date', 4, 6))  # 2 error, 50% error
#         mae_error = error_calculations.mae(data)
#         mape_error = error_calculations.mape(data)
#         self.assertTrue(mae_error - 1.5 < 0.001, "Mae error should be very close to 1.5")
#         self.assertEqual(mape_error, 75)
#
# if __name__ == '__main__':
#     unittest.main()
