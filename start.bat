@echo off
echo Starting Ollama AI Engine...
start "Ollama Engine" cmd /c "ollama run llama3.2:latest"

echo Waiting 5 seconds for AI to spin up...
timeout /t 5 /nobreak > NUL

echo Starting Crypto Trading Bot...
set PYTHONPATH=.
python bot/main.py
