#!/bin/sh

# Apply other migrations
python manage.py migrate ImageUploader 0001_initial
python manage.py migrate ImageUploader 0002_auto_20230220_1810

# Create the superuser with default account tier
python manage.py create_superuser --username admin123 --email a@a.com --password admin --account_tier "Basic"

# Start the server
python manage.py runserver 0.0.0.0:8000