@echo off
:: run.bat — Shortcut to run any Python script using the correct Python
:: ─────────────────────────────────────────────────────────────────────
:: USAGE (from the project folder):
::   run.bat test_fetcher.py
::   run.bat news_fetcher.py
::   run.bat main.py
::
:: This exists because Windows has a "python" alias that redirects
:: to the Microsoft Store instead of your real Python installation.
:: This batch file bypasses that alias by using the full path directly.

SET PYTHON=C:\Users\badhe\AppData\Local\Python\pythoncore-3.14-64\python.exe

IF "%1"=="" (
    echo Usage: run.bat ^<script.py^>
    echo Example: run.bat test_fetcher.py
    exit /b 1
)

"%PYTHON%" %*
