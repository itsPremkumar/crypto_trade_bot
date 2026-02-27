@echo off
echo Cleaning up existing bot processes...
:: Kill by window title first
taskkill /F /FI "WINDOWTITLE eq Crypto Trading Bot" /T 2>NUL
:: Kill by image name and command line check (powershell fallback)
powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*bot/main.py*' } | Stop-Process -Force -ErrorAction SilentlyContinue"

echo Starting Ollama AI Engine...
start "Ollama Engine" cmd /c "ollama run llama3.2:latest"

echo Waiting 5 seconds for AI to spin up...
timeout /t 5 /nobreak > NUL

echo Starting Crypto Trading Bot...
set PYTHONPATH=.
:: Set title so we can kill it later if needed
title Crypto Trading Bot
python bot/main.py
