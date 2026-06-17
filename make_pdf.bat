@echo off
chcp 65001 >nul
setlocal
cd /d "C:\Users\infomax\Documents\Report"
set PYTHONIOENCODING=utf-8

echo.
echo [2] CEO 보고용 PDF 생성
echo.

python -c "from google import genai" 2>nul
if errorlevel 1 (
    echo 필요 패키지 설치 중...
    pip install -r requirements.txt
)

python make_pdf.py
set CODE=%ERRORLEVEL%
if %CODE% neq 0 (
    echo.
    echo [오류] PDF 생성 실패
    pause
    exit /b %CODE%
)

echo.
pause
exit /b 0
