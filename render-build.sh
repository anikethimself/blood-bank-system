#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Initialize data (runs on every deploy, but script handles duplicates)
python create_admin.py
python init_stock.py
