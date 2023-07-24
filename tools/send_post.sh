#!/bin/sh

BASEDIR=$(dirname "$0")

curl -X POST -H "Content-Type: application/json" -d @${BASEDIR}/example.json http://localhost:5000/convert
