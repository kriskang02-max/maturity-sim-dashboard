@echo off
chcp 65001 >nul
setlocal
cd /d "C:\Users\infomax\Documents\Report"
set PYTHONIOENCODING=utf-8

echo.
echo 패키지 설치 중...
pip install -r requirements.txt
echo.
echo 완료.
pause
