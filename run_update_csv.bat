@echo off
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "%~dp0update_minyoung_csv.ps1"
pause
