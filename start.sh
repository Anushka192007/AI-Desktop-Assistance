#!/bin/bash

export FLASK_APP=app.py
export FLASK_ENV=development

# Load environment variables from .env
export $(cat .env | xargs)

flask run
