#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create admin user (Alternative to Shell)
python create_admin.py

# Ensure uploads directory exists
mkdir -p uploads
