import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask.testing import FlaskClient
from exchangeapi import app

class TestConversionEndpoint(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.mock_get_exchange_rate = MagicMock(return_value=1.4)
        self.mock_get_exchange_rate_failure = MagicMock(return_value=None)

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

            self.assertEqual(response.status_code, 200)
            response_data = response.get_json()
            self.assertIn('transaction_id', response_data)
            self.assertEqual(response_data['user_id'], test_data['user_id'])
            self.assertEqual(response_data['source_currency'], test_data['source_currency'])
            self.assertEqual(response_data['amount'], test_data['amount'])
            self.assertEqual(response_data['target_currency'], test_data['target_currency'])
            self.assertEqual(response_data['converted_amount'], 140)
            self.assertEqual(response_data['exchange_rate'], 1.4)
            self.assertIsNotNone(response_data['timestamp'])

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

            self.assertEqual(response.status_code, 400)
            response_data = response.get_json()
            self.assertEqual(response_data['message'], 'user id "0" is not allowed!')

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

            self.assertEqual(response.status_code, 400)
            response_data = response.get_json()
            self.assertEqual(response_data['message'], 'Invalid amount. amount must be a positive number')

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

            self.assertEqual(response.status_code, 400)
            response_data = response.get_json()
            self.assertEqual(response_data['message'], 'Invalid amount. amount must be a positive number')

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

            self.assertEqual(response.status_code, 400)
            response_data = response.get_json()
            self.assertEqual(response_data['message'], 'WTF is not supported!')

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

            self.assertEqual(response.status_code, 400)
            response_data = response.get_json()
            self.assertEqual(response_data['message'], 'WTF is not supported!')

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

            self.assertEqual(response.status_code, 400)
            response_data = response.get_json()
            self.assertEqual(response_data['message'], 'failure getting exchange rate on the external API')

if __name__ == '__main__':
    unittest.main()
