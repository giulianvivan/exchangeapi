#!/bin/sh

export FLASK_APP=exchangeapi
export FLASK_ENV=development

python database.py

flask run
