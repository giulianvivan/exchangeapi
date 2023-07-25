from datetime import datetime
from flask import Flask, request, abort, jsonify
from flask_restful import Api, Resource
from database import DatabaseHandler

app = Flask(__name__)
api = Api(app)

# database setup
dbh = DatabaseHandler()
dbh.create_tables()

SUPPORTED_CURRENCIES = ('BRL', 'USD', 'EUR', 'JPY')
ALLOWED_USERS = { 1, 'John Doe',
                  2, 'Jane Doe' }

def get_exchange_rate(source_currency, target_currency):
    return 1.2

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

        if source_currency not in SUPPORTED_CURRENCIES:
            abort(400, description=f'{source_currency} is not supported!')

        if target_currency not in SUPPORTED_CURRENCIES:
            abort(400, description=f'{target_currency} is not supported!')

        exchange_rate = get_exchange_rate(source_currency, target_currency)
        if not isinstance(exchange_rate, (int, float)):
            abort(400, description='failure getting exchange rate on the external API')

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
