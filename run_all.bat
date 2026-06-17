@echo off
chcp 65001 >nul
setlocal
cd /d "C:\Users\infomax\Documents\Report"
set PYTHONIOENCODING=utf-8

echo.
echo ========================================
echo   채권 모닝브리핑 (추출 + PDF)
echo ========================================
echo.

python run_all.py
set CODE=%ERRORLEVEL%
if %CODE% neq 0 (
    echo.
    echo [오류] 종료 코드: %CODE%
    pause
    exit /b %CODE%
)

echo.
pause
exit /b 0
