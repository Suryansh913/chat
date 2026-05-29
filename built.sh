#!/bin/bash
set -e

# Install with pre-built wheels only (no compilation)
pip install --only-binary :all: -r requirements.txt

# Run Django migrations and collectstatic
python manage.py migrate
python manage.py collectstatic --noinput
