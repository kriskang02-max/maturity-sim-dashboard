@echo off
chcp 65001 >nul
setlocal

cd /d "C:\Users\infomax\Documents\Report"
set PYTHONIOENCODING=utf-8

echo.
echo .env 파일을 엽니다. 아래 중 하나의 API 키를 추가하세요:
echo.
echo   CURSOR_API_KEY=cursor_...   (Cursor Dashboard - Integrations)
echo   GEMINI_API_KEY=...          (Google AI Studio, 무료)
echo   OPENAI_API_KEY=sk-...
echo.

if not exist ".env" (
    copy ".env.example" ".env" >nul
)

notepad ".env"
echo.
python check_llm.py
pause
