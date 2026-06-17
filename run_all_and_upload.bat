@echo off
chcp 65001 >nul
setlocal
cd /d "C:\Users\infomax\Documents\Report"
set PYTHONIOENCODING=utf-8

set "UPLOAD_BAT=C:\Users\infomax\Documents\market_db_dashboard\push_briefing_pdf.bat"

echo.
echo ========================================
echo   채권 모닝브리핑 (추출 + PDF + 업로드)
echo ========================================
echo.

echo === 1/2 텔레그램 추출 및 PDF 생성 ===
echo.
python run_all.py
set "CODE=%ERRORLEVEL%"
if %CODE% neq 0 (
  echo.
  echo [오류] PDF 생성 실패 ^(종료 코드: %CODE%^)
  pause
  exit /b %CODE%
)

echo.
echo === 2/2 대시보드 업로드 ===
echo.
if not exist "%UPLOAD_BAT%" (
  echo [오류] 업로드 스크립트를 찾을 수 없습니다:
  echo   %UPLOAD_BAT%
  pause
  exit /b 1
)

call "%UPLOAD_BAT%"
set "UPLOAD_CODE=%ERRORLEVEL%"
if %UPLOAD_CODE% neq 0 (
  echo.
  echo [오류] 업로드 실패 ^(종료 코드: %UPLOAD_CODE%^)
  pause
  exit /b %UPLOAD_CODE%
)

echo.
echo === 전체 완료 ===
pause
exit /b 0
