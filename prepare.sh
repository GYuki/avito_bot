#!/bin/sh

python webhook.py https://5d46c47c.ngrok.io
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
