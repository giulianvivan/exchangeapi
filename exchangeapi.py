from datetime import datetime
from flask import Flask, request, abort
from flask_restful import Api, Resource
from database import DatabaseHandler

app = Flask(__name__)
api = Api(app)

# database setup
dbh = DatabaseHandler()
dbh.create_tables()

# FIXME: temporarily hardcoded for easiness
SUPPORTED_CURRENCIES = ('BRL', 'USD', 'EUR', 'JPY')
ALLOWED_USERS = { 1, 'John Doe',
                  2, 'Jane Doe' }

def get_exchange_rate(source_currency, target_currency):
    # TODO: implement the requests to http://api.exchangeratesapi.io/latest?base=EUR
    # for now, returning a fixed 1.2 rate
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

api.add_resource(ConversionResource, '/convert')
