#!/bin/sh
set -euo pipefail

echo "Running database initialization scripts..."
python ./init_db.py

echo "Starting the application..."
python ./main.py