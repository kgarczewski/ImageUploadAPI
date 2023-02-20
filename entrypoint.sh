#!/bin/sh

# Apply other migrations
python manage.py migrate ImageUploader 0001_initial
python manage.py migrate ImageUploader 0002_auto_20230220_1810

# Start the server
python manage.py runserver 0.0.0.0:8000