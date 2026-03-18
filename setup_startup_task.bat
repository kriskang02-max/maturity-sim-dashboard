@echo off
REM 로그인 시 yield_table CSV 자동 갱신 + GitHub 푸시 작업 등록
REM 관리자 권한 불필요. 한 번만 실행하면 됩니다.

cd /d "%~dp0"
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set TASK_NAME=YieldTable_CSV_GitHub_AutoUpdate
set TRIGGER=onlogon
set "TR=powershell -ExecutionPolicy Bypass -WindowStyle Hidden -NoProfile -File ""%SCRIPT_DIR%\auto_update_and_push.ps1"""

echo Registering scheduled task...
echo Task name: %TASK_NAME%
echo Trigger: At user logon
echo Action: Run yield_table.xlsm then git push
echo.

schtasks /create /tn "%TASK_NAME%" /tr "%TR%" /sc %TRIGGER% /f

if errorlevel 1 (
    echo Failed to create task. Check schtasks error above.
    pause
    exit /b 1
)

echo.
echo Done. CSV will auto-update and push to GitHub on each logon.
echo Log folder: %SCRIPT_DIR%\logs\
echo To remove task: schtasks /delete /tn "%TASK_NAME%" /f
echo.
pause
