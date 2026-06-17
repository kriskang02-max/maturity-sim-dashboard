@echo off
chcp 65001 >nul
setlocal
cd /d "C:\Users\infomax\Documents\Report"
set PYTHONIOENCODING=utf-8

echo.
echo [1] 텔레그램 raw 추출 (9개 대화)
echo.

python fetch_raw.py
set CODE=%ERRORLEVEL%
if %CODE% neq 0 (
    echo.
    echo [오류] 추출 실패
    pause
    exit /b %CODE%
)

echo.
pause
exit /b 0
