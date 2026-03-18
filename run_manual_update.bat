@echo off
REM CSV 갱신 + GitHub 푸시 수동 실행 (로그인 시 자동 실행과 동일)
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0auto_update_and_push.ps1"
pause
