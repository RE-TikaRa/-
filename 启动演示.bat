@echo off
setlocal
cd /d "%~dp0"
uv run python src\main.py
pause
