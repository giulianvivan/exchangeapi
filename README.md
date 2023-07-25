# exchangeapi

This project is an API for currency exchange. Backend only. (assuming MVC, no view was implemented)

* written in Python/Flask
* SQLite is used as database
* Flask-RESTful used for easiness of development
* 'requests' package used to call the external API
* 'unittest' package used for testing
* 'unittest.mock' was heavily used on tests
* 'freezegun' package used to test 'datetime'/timestamp

## Project structure

├── requirements.txt: Contains all required python packages for this project.

├── database.py: Contains SQLite access implementation for this project. (assuming MVC, this is the model layer)

├── exchangeapi.py: Contains the project core implementation. (assuming MVC, this is the controller layer)

* Conversion endpoint (Flask-RESTful Resource): implements the conversion logic
* User transactions endpoint (Flask-RESTful Resource): gets all transactions (currency conversions) from the database for a given user id
* get_exchange_rate function: make the call to the external API to get the exchange rate

├── tests: Contains all unit tests

└── tools: Contains tools to make the development easier
* run_dev.sh: a script that runs the development server with some predefined vars
* example.json: a json for testing the server
* send_post.sh: a script to post the 'example.json' into the server Conversion endpoint

## Install instructions (GNU/Linux)

Of course, there are many ways to do it. The simplest is:

1. Setup your virtual environment
2. pip install -r requirements.txt
3. export ACCESS_KEY="your real key for the external API"
4. ./tools/run_dev.sh

## Endpoints

### Conversion
* path: "/convert"
* method: POST
* expects: a json containing:
  * user_id: int
  * source_currency: string
  * target_currency: string
  * amount: float
* returns: a json containing the transaction details or an error message
  * if success (status code 200):
    * transaction_id: int
    * user_id: int
    * source_currency: string
    * amount: float
    * target_currency: string
    * converted_amount: float
    * exchange_rate: float
    * timestamp: string
  * if error (status code 400):
    * message: string

### User transactions
* path: "/transactions/<user_id>"
* method: GET
* expects: the user id from which the transactions will be retrieved from the database
* returns: a json containing a list of all transactions of the given user
  * each transaction object contains:
    * transaction_id: int
    * user_id: int
    * source_currency: string
    * amount: float
    * target_currency: string
    * converted_amount: float
    * exchange_rate: float
    * timestamp: string
