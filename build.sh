#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Ensure uploads directory exists (equivalent to app.use('/uploads', express.static('uploads')))
mkdir -p uploads
