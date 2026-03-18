@echo off
cd /d "%~dp0"
REM Python이 PATH에 없을 때 사용. 설치 경로를 그대로 사용합니다.
"C:\Users\infomax\AppData\Local\Python\bin\python.exe" -m http.server 8000
pause
