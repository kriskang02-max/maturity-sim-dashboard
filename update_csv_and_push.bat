@echo off
REM 만기매칭형 시뮬레이션 대시보드용 CSV 업데이트 배치
REM 1) yield_table.csv를 새 파일로 덮어쓴 뒤
REM 2) 이 배치 파일을 더블클릭해서 실행하세요.

cd /d "%~dp0"

echo [1/3] Git 상태 확인 중...
git status >NUL 2>&1
if errorlevel 1 (
    echo Git 저장소가 아니거나 git이 PATH에 없습니다.
    echo 먼저 이 폴더에서 git init 및 git 설치를 확인하세요.
    pause
    goto :eof
)

echo [2/3] CSV 변경사항 스테이징 중...
git add "yield_table.csv"

for /f "tokens=1-3 delims=/ " %%a in ("%date%") do (
    set TODAY=%%a-%%b-%%c
)

set MSG=Update daily CSV %TODAY%

echo [3/3] 커밋 및 푸시 중...
git commit -m "%MSG%" && git push

if errorlevel 1 (
    echo.
    echo 푸시 과정에서 오류가 발생했습니다. 위 메시지를 확인해주세요.
) else (
    echo.
    echo 완료되었습니다. GitHub Pages가 잠시 후 최신 CSV로 갱신됩니다.
)

pause

