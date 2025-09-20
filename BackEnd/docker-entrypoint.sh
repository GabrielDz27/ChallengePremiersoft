#!/bin/sh
set -e

echo "Running database initialization scripts..."
python ./init_db.py
python ./processa_planilhas.py

echo "Starting the application..."
python ./main.py