#!/bin/sh
set -e

python /app/init_db.py
python /app/processa_planilhas.py
python /app/main.py
