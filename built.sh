#!/bin/bash
set -e

# Install with pre-built wheels only
pip install --prefer-binary -r requirements.txt

# Run Django setup
python manage.py migrate
python manage.py collectstatic --noinput