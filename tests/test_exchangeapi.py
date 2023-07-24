import unittest
from unittest.mock import patch, MagicMock
from freezegun import freeze_time
from flask import Flask
from flask.testing import FlaskClient
from exchangeapi import app, dbh
from database import DatabaseHandler

TRANSACTION_ID = 123

class TestConversionEndpoint(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.mock_get_exchange_rate = MagicMock(return_value=1.4)
        self.mock_get_exchange_rate_failure = MagicMock(return_value=None)

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

            # assert persistency
            dbh.create_tables.assert_not_called()
            dbh.insert_transaction.assert_not_called()
            dbh.get_user_transactions.assert_not_called()

    @patch.object(dbh, 'create_tables', MagicMock(return_value=None))
    @patch.object(dbh, 'insert_transaction', MagicMock(return_value=TRANSACTION_ID))
    @patch.object(dbh, 'get_user_transactions', MagicMock(return_value=[]))
    def test_conversion_endpoint_with_source_currency_not_supported(self):
        # Prepare the test data
        test_data = {
            'user_id': 1,
            'source_currency': 'WTF',
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
            self.assertEqual(response_data['message'], 'WTF is not supported!')

            # assert persistency
            dbh.create_tables.assert_not_called()
            dbh.insert_transaction.assert_not_called()
            dbh.get_user_transactions.assert_not_called()

    @patch.object(dbh, 'create_tables', MagicMock(return_value=None))
    @patch.object(dbh, 'insert_transaction', MagicMock(return_value=TRANSACTION_ID))
    @patch.object(dbh, 'get_user_transactions', MagicMock(return_value=[]))
    def test_conversion_endpoint_with_target_currency_not_supported(self):
        # Prepare the test data
        test_data = {
            'user_id': 1,
            'source_currency': 'EUR',
            'target_currency': 'WTF',
            'amount': 100
        }

        # Mock the get_exchange_rate function
        with patch('exchangeapi.get_exchange_rate', self.mock_get_exchange_rate):
            # Send a POST request to the conversion endpoint
            response = self.app.post('/convert', json=test_data)

            # assert communication
            self.assertEqual(response.status_code, 400)
            response_data = response.get_json()
            self.assertEqual(response_data['message'], 'WTF is not supported!')

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
            self.assertEqual(response_data['message'], 'failure getting exchange rate on the external API')

            # assert persistency
            dbh.create_tables.assert_not_called()
            dbh.insert_transaction.assert_not_called()
            dbh.get_user_transactions.assert_not_called()

# FIXME: this would be better being local
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

if __name__ == '__main__':
    unittest.main()
