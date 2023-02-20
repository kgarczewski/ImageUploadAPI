#!/bin/sh

# Apply other migrations
python manage.py migrate ImageUploader 0001_initial
python manage.py migrate ImageUploader 0002_create_plans
python manage.py migrate ImageUploader 0003_customuser

# Start the server
python manage.py runserver 0.0.0.0:8000