# PC 로그인 시 자동 실행: yield_table.xlsm으로 CSV 갱신 후 GitHub 푸시
# 작업 스케줄러에서 "사용자 로그온 시" 이 스크립트를 실행하도록 등록하면 됩니다.

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$excelPath = Join-Path $scriptDir "yield_table.xlsm"
$logDir = Join-Path $scriptDir "logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$logFile = Join-Path $logDir "auto_update_$(Get-Date -Format 'yyyyMMdd').log"

function Log { param($msg) $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg"; Write-Host $line; Add-Content -Path $logFile -Value $line -ErrorAction SilentlyContinue }

try {
    Log "=== 자동 갱신 시작 ==="

    # 1) CSV 갱신: yield_table.xlsm 실행 후 매크로가 저장·종료할 때까지 대기
    if (-not (Test-Path $excelPath)) {
        Log "오류: 파일 없음 - $excelPath"
        exit 1
    }
    Log "엑셀 실행 중 (매크로 완료 시까지 대기)..."
    $p = Start-Process -FilePath $excelPath -PassThru -Wait -WorkingDirectory $scriptDir
    Log "엑셀 종료됨 (종료코드: $($p.ExitCode))."

    # CSV 파일 쓰기 완료 대기 (엑셀 종료 후 디스크 반영 시간)
    $delaySeconds = 15
    Log "CSV 반영 대기 중 ($delaySeconds 초)..."
    Start-Sleep -Seconds $delaySeconds

    # 2) Git 푸시
    $gitOk = $false
    git status 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Log "오류: 이 폴더는 Git 저장소가 아니거나 git이 PATH에 없습니다."
        exit 1
    }

    git add "yield_table.csv"
    $today = Get-Date -Format "yyyy-MM-dd"
    $msg = "Update daily CSV $today"
    git commit -m $msg 2>&1 | ForEach-Object { Log $_ }
    if ($LASTEXITCODE -eq 0) {
        git push 2>&1 | ForEach-Object { Log $_ }
        if ($LASTEXITCODE -eq 0) { $gitOk = $true }
    } else {
        Log "커밋할 변경 없음 또는 커밋 오류."
        # 변경 없으면 성공으로 간주
        $gitOk = $true
    }

    if ($gitOk) {
        Log "완료. GitHub Pages에서 잠시 후 최신 데이터를 볼 수 있습니다."
    } else {
        Log "푸시 실패. 네트워크 또는 Git 인증을 확인하세요."
        exit 1
    }
} catch {
    Log "예외: $_"
    exit 1
}

Log "=== 자동 갱신 끝 ==="
