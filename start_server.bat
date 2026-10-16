@echo off
echo Starting Career Guidance Platform...
cd /d "%~dp0"
call .venv\Scripts\python.exe start_platform.py
pause