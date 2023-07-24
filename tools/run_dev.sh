#!/bin/sh

PROJECT_DIR="$(dirname "$0")/.."

export FLASK_APP=$PROJECT_DIR/exchangeapi
export FLASK_ENV=development

python $PROJECT_DIR/database.py

flask run
