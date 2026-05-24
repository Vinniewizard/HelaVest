#!/bin/bash

echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear

echo "Static files collected successfully."
