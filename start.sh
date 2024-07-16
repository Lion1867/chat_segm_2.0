#!/bin/bash

# Запуск FastAPI приложения
uvicorn fast_api:app --host 0.0.0.0 --port 8080 &

# Запуск скрипта main.py
python3 main.py