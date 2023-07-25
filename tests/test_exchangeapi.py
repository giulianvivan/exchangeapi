import unittest, requests, os
from unittest.mock import patch, MagicMock
from freezegun import freeze_time
from flask import Flask
from flask.testing import FlaskClient
from exchangeapi import app, dbh, get_exchange_rate
from database import DatabaseHandler

TRANSACTION_ID = 123

class TestConversionEndpoint(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.mock_get_exchange_rate = MagicMock(return_value=1.4)
        self.mock_get_exchange_rate_failure = MagicMock()
        self.mock_get_exchange_rate_failure.side_effect = RuntimeError("failure getting exchange rate on the external API. Status Code: 500")

    @freeze_time("2023-07-24 22:30:00", tz_offset=-3)
    @patch.object(dbh, 'create_tables', MagicMock(return_value=None))
    @patch.object(dbh, 'insert_transaction', MagicMock(return_value=TRANSACTION_ID))
    @patch.object(dbh, 'get_user_transactions', MagicMock(return_value=[]))
    def test_conversion_endpoint_success(self):
        # Prepare the test data
        test_data = {
            'user_id': 1,
            'source_currency': 'EUR',
            'target_currency': 'USD',
            'amount': 100
        }

        # Mock the get_exchange_rate function
        with patch('exchangeapi.get_exchange_rate', self.mock_get_exchange_rate):
            # Send a POST request to the conversion endpoint
            response = self.app.post('/convert', json=test_data)

            # assert communication
            self.assertEqual(response.status_code, 200)
            response_data = response.get_json()
            self.assertEqual(response_data['transaction_id'], TRANSACTION_ID)
            self.assertEqual(response_data['user_id'], test_data['user_id'])
            self.assertEqual(response_data['source_currency'], test_data['source_currency'])
            self.assertEqual(response_data['amount'], test_data['amount'])
            self.assertEqual(response_data['target_currency'], test_data['target_currency'])
            self.assertEqual(response_data['converted_amount'], 140)
            self.assertEqual(response_data['exchange_rate'], 1.4)
            self.assertIsNotNone(response_data['timestamp'])
            self.mock_get_exchange_rate.assert_called_once_with(test_data['source_currency'],
                                                                test_data['target_currency'])

            # assert persistency
            dbh.create_tables.assert_not_called()
            dbh.insert_transaction.assert_called_once_with(test_data['user_id'],
                                                           test_data['source_currency'],
                                                           test_data['amount'],
                                                           test_data['target_currency'],
                                                           140,
                                                           1.4,
                                                           '2023-07-24T19:30:00Z')
            dbh.get_user_transactions.assert_not_called()

    @patch.object(dbh, 'create_tables', MagicMock(return_value=None))
    @patch.object(dbh, 'insert_transaction', MagicMock(return_value=TRANSACTION_ID))
    @patch.object(dbh, 'get_user_transactions', MagicMock(return_value=[]))
    def test_conversion_endpoint_with_invalid_user(self):
        # Prepare the test data
        test_data = {
            'user_id': 0,
            'source_currency': 'EUR',
            'target_currency': 'USD',
            'amount': 100
        }

        # Mock the get_exchange_rate function
        with patch('exchangeapi.get_exchange_rate', self.mock_get_exchange_rate):
            # Send a POST request to the conversion endpoint
            response = self.app.post('/convert', json=test_data)

            # assert communication
            self.assertEqual(response.status_code, 400)
            response_data = response.get_json()
            self.assertEqual(response_data['message'], 'user id "0" is not allowed!')
            self.mock_get_exchange_rate.assert_not_called()

            # assert persistency
            dbh.create_tables.assert_not_called()
            dbh.insert_transaction.assert_not_called()
            dbh.get_user_transactions.assert_not_called()

    @patch.object(dbh, 'create_tables', MagicMock(return_value=None))
    @patch.object(dbh, 'insert_transaction', MagicMock(return_value=TRANSACTION_ID))
    @patch.object(dbh, 'get_user_transactions', MagicMock(return_value=[]))
    def test_conversion_endpoint_with_negative_amount(self):
        # Prepare the test data
        test_data = {
            'user_id': 1,
            'source_currency': 'EUR',
            'target_currency': 'USD',
            'amount': -100
        }

        # Mock the get_exchange_rate function
        with patch('exchangeapi.get_exchange_rate', self.mock_get_exchange_rate):
            # Send a POST request to the conversion endpoint
            response = self.app.post('/convert', json=test_data)

            # assert communication
            self.assertEqual(response.status_code, 400)
            response_data = response.get_json()
            self.assertEqual(response_data['message'], 'Invalid amount. amount must be a positive number')
            self.mock_get_exchange_rate.assert_not_called()

            # assert persistency
            dbh.create_tables.assert_not_called()
            dbh.insert_transaction.assert_not_called()
            dbh.get_user_transactions.assert_not_called()

    @patch.object(dbh, 'create_tables', MagicMock(return_value=None))
    @patch.object(dbh, 'insert_transaction', MagicMock(return_value=TRANSACTION_ID))
    @patch.object(dbh, 'get_user_transactions', MagicMock(return_value=[]))
    def test_conversion_endpoint_with_zero_amount(self):
        # Prepare the test data
        test_data = {
            'user_id': 1,
            'source_currency': 'EUR',
            'target_currency': 'USD',
            'amount': 0
        }

        # Mock the get_exchange_rate function
        with patch('exchangeapi.get_exchange_rate', self.mock_get_exchange_rate):
            # Send a POST request to the conversion endpoint
            response = self.app.post('/convert', json=test_data)

            # assert communication
            self.assertEqual(response.status_code, 400)
            response_data = response.get_json()
            self.assertEqual(response_data['message'], 'Invalid amount. amount must be a positive number')
            self.mock_get_exchange_rate.assert_not_called()

            # assert persistency
            dbh.create_tables.assert_not_called()
            dbh.insert_transaction.assert_not_called()
            dbh.get_user_transactions.assert_not_called()

    @patch.object(dbh, 'create_tables', MagicMock(return_value=None))
    @patch.object(dbh, 'insert_transaction', MagicMock(return_value=TRANSACTION_ID))
    @patch.object(dbh, 'get_user_transactions', MagicMock(return_value=[]))
    def test_conversion_endpoint_with_external_API_failure(self):
        # Prepare the test data
        test_data = {
            'user_id': 1,
            'source_currency': 'EUR',
            'target_currency': 'USD',
            'amount': 100
        }

        # Mock the get_exchange_rate function
        with patch('exchangeapi.get_exchange_rate', self.mock_get_exchange_rate_failure):
            # Send a POST request to the conversion endpoint
            response = self.app.post('/convert', json=test_data)

            # assert communication
            self.assertEqual(response.status_code, 400)
            response_data = response.get_json()
            self.assertEqual(response_data['message'], 'failure getting exchange rate on the external API. Status Code: 500')
            self.mock_get_exchange_rate_failure.assert_called_once_with(test_data['source_currency'],
                                                                        test_data['target_currency'])

            # assert persistency
            dbh.create_tables.assert_not_called()
            dbh.insert_transaction.assert_not_called()
            dbh.get_user_transactions.assert_not_called()

TEST_DATA = [
            {
                'transaction_id': 1,
                'user_id': 1,
                'source_currency': 'USD',
                'amount': 100,
                'target_currency': 'EUR',
                'converted_amount': 85,
                'exchange_rate': 0.85,
                'timestamp': '2023-07-21T12:34:56Z'
            },
            {
                'transaction_id': 2,
                'user_id': 1,
                'source_currency': 'EUR',
                'amount': 50,
                'target_currency': 'USD',
                'converted_amount': 58.82,
                'exchange_rate': 1.1764,
                'timestamp': '2023-07-22T09:15:00Z'
            }
        ]

class TestUserTransactionsEndpoint(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    @patch.object(dbh, 'create_tables', MagicMock(return_value=None))
    @patch.object(dbh, 'insert_transaction', MagicMock(return_value=TRANSACTION_ID))
    @patch.object(dbh, 'get_user_transactions', MagicMock(return_value=TEST_DATA))
    def test_user_transaction_endpoint_success(self):
        user_id = 1

        # send a GET request to the user transactions endpoint
        response = self.app.get(f'/transactions/{user_id}')

        # assert communication
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(response_data, TEST_DATA)

        # assert persistency
        dbh.create_tables.assert_not_called()
        dbh.insert_transaction.assert_not_called()
        dbh.get_user_transactions.assert_called_once_with(1)

API_RESPONSE_SUCCESS_JSON = '''
{
  "success": true,
  "timestamp": 1690310823,
  "base": "EUR",
  "date": "2023-07-25",
  "rates": {
            "BOB": 7.631912, "BRL": 5.244123, "BSD": 1.104602,
            "BTC": 3.7687642e-05, "BTN": 90.352454, "BWP": 14.418964,
            "CAD": 1.454466, "CDF": 2744.066964, "CHF": 0.954935,
            "CLF": 0.033161, "CLP": 915.005099, "CNY": 7.880275,
            "ETB": 60.408105, "EUR": 1, "FJD": 2.456685,
            "FKP": 0.860849, "GBP": 0.856933, "GEL": 2.865519,
            "JOD": 0.782929, "JPY": 155.787685, "KES": 156.969635,
            "NOK": 11.112199, "NPR": 144.565636, "NZD": 1.773943,
            "USD": 1.104252, "UYU": 41.948185, "UZS": 12820.368178,
            "ZMW": 21.344753, "ZWL": 355.568764
           }
}
'''

API_RESPONSE_FAILURE_JSON = '''
{
  "success": false,
  "error": {
            "code": 101,
            "type": "invalid_access_key",
            "info": "You have not supplied a valid API Access Key"
           }
}
'''

@patch.dict(os.environ, {"ACCESS_KEY": "123key456"})
class TestGetExchangeRateFunction(unittest.TestCase):
    def setUp(self):
        r = requests.Response()
        r.status_code = 200
        r.encoding = 'UTF-8'
        r._content = API_RESPONSE_SUCCESS_JSON.encode(r.encoding)
        self.mock_requests_get = MagicMock(return_value=r)

        r = requests.Response()
        r.status_code = 500
        self.mock_requests_get_with_internal_server_error = MagicMock(return_value=r)

        r = requests.Response()
        r.status_code = 200
        r.encoding = 'UTF-8'
        r._content = API_RESPONSE_FAILURE_JSON.encode(r.encoding)
        self.mock_requests_get_with_other_server_error = MagicMock(return_value=r)

    def test_get_exchange_rate_success(self):
        # Mock the requests.get() function
        with patch('requests.get', self.mock_requests_get):
            exchange_rate = get_exchange_rate('EUR', 'USD')

        self.assertEqual(exchange_rate, 1.104252)
        self.mock_requests_get.assert_called_once_with('http://api.exchangeratesapi.io/latest?base=EUR&access_key=123key456')

    def test_get_exchange_rate_with_source_currency_not_supported(self):
        with self.assertRaises(ValueError) as cm:
            exchange_rate = get_exchange_rate('USD', 'BRL')

        self.assertEqual(str(cm.exception), 'free API supports only EUR as base currency')

    def test_get_exchange_rate_with_target_currency_not_supported(self):
        # Mock the requests.get() function
        with patch('requests.get', self.mock_requests_get):
            with self.assertRaises(ValueError) as cm:
                exchange_rate = get_exchange_rate('EUR', 'WTF')

            self.assertEqual(str(cm.exception), 'exchange rate for WTF not available in the external API response')
            self.mock_requests_get.assert_called_once_with('http://api.exchangeratesapi.io/latest?base=EUR&access_key=123key456')

    def test_get_exchange_rate_with_api_call_internal_server_error(self):
        # Mock the requests.get() function
        with patch('requests.get', self.mock_requests_get_with_internal_server_error):
            with self.assertRaises(RuntimeError) as cm:
                exchange_rate = get_exchange_rate('EUR', 'USD')

            self.assertEqual(str(cm.exception), "failure getting exchange rate on the external API. Status Code: 500")
            self.mock_requests_get_with_internal_server_error.assert_called_once_with('http://api.exchangeratesapi.io/latest?base=EUR&access_key=123key456')

    def test_get_exchange_rate_with_api_call_other_server_error(self):
        # Mock the requests.get() function
        with patch('requests.get', self.mock_requests_get_with_other_server_error):
            with self.assertRaises(ValueError) as cm:
                exchange_rate = get_exchange_rate('EUR', 'USD')

            self.assertEqual(str(cm.exception), "failure getting exchange rate on the external API. Error: {'code': 101, 'type': 'invalid_access_key', 'info': 'You have not supplied a valid API Access Key'}")
            self.mock_requests_get_with_other_server_error.assert_called_once_with('http://api.exchangeratesapi.io/latest?base=EUR&access_key=123key456')

if __name__ == '__main__':
    unittest.main()
