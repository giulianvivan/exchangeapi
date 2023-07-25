import requests, os
from datetime import datetime
from flask import Flask, request, abort, jsonify
from flask_restful import Api, Resource
from database import DatabaseHandler

app = Flask(__name__)
api = Api(app)

# database setup
dbh = DatabaseHandler()
dbh.create_tables()

ALLOWED_USERS = { 1, 'John Doe',
                  2, 'Jane Doe' }

def get_exchange_rate(source_currency, target_currency):
    access_key = os.environ['ACCESS_KEY']

    # the free API key allows only rates based on EUR (remove this
    # check if your key is supports other currencies)
    if source_currency != 'EUR':
        raise ValueError(f"free API supports only EUR as base currency")

    api_url = f'http://api.exchangeratesapi.io/latest?base={source_currency}&access_key={access_key}'

    response = requests.get(api_url)

    if response.status_code == 200:
        response_data = response.json()

        if response_data['success'] is True:
            exchange_rate = response_data['rates'].get(target_currency)
            if exchange_rate is not None:
                return exchange_rate
            else:
                # 'target_currency' not found in the response data
                raise ValueError(f"exchange rate for {target_currency} not available in the external API response")
        else:
            # API call failed by value
            raise ValueError(f"failure getting exchange rate on the external API. Error: {response_data['error']}")
    else:
        # API call failed by status code
        raise RuntimeError(f"failure getting exchange rate on the external API. Status Code: {response.status_code}")

class ConversionResource(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        source_currency = data.get('source_currency')
        target_currency = data.get('target_currency')
        amount = data.get('amount')

        if user_id not in ALLOWED_USERS:
            abort(400, description=f'user id "{user_id}" is not allowed!')

        if not isinstance(amount, (int, float)) or amount <= 0:
            abort(400, description='Invalid amount. amount must be a positive number')

        try:
            exchange_rate = get_exchange_rate(source_currency, target_currency)
        except Exception as e:
            abort(400, description=f'{e}')

        converted_amount = amount * exchange_rate

        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        transaction_id = dbh.insert_transaction(user_id,
                                                source_currency,
                                                amount,
                                                target_currency,
                                                converted_amount,
                                                exchange_rate,
                                                timestamp)

        return {
            'transaction_id': transaction_id,
            'user_id': user_id,
            'source_currency': source_currency,
            'amount': amount,
            'target_currency': target_currency,
            'converted_amount': converted_amount,
            'exchange_rate': exchange_rate,
            'timestamp': timestamp
        }, 200

class UserTransactionsResource(Resource):
    def get(self, user_id):
        # retrieve user transactions from the database
        transactions = dbh.get_user_transactions(user_id)

        # return the transactions as a list of dictionaries
        return jsonify(transactions)

api.add_resource(ConversionResource, '/convert')
api.add_resource(UserTransactionsResource, '/transactions/<int:user_id>')
