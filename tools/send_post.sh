#!/bin/sh

BASEDIR=$(dirname "$0")

curl -X POST -H "Content-Type: application/json" -d @${BASEDIR}/example.json https://exchangeapi-f2v1.onrender.com/convert
