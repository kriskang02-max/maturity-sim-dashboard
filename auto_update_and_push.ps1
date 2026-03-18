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
    $excelExitTime = Get-Date
    Log "엑셀 종료됨 (종료코드: $($p.ExitCode))."

    $csvPath = Join-Path $scriptDir "yield_table.csv"
    # CSV 파일이 엑셀 실행 중/직후에 쓰였는지 확인 (종료 시각 기준 2분 이내 수정이면 반영된 것으로 봄)
    Start-Sleep -Seconds 10
    $csvReady = $false
    $cutoff = $excelExitTime.AddSeconds(-120)
    for ($i = 1; $i -le 6; $i++) {
        if (Test-Path $csvPath) {
            $csvItem = Get-Item $csvPath
            $lastWrite = $csvItem.LastWriteTime
            if ($lastWrite -ge $cutoff) {
                $csvReady = $true
                Log "yield_table.csv ready (last write: $($lastWrite.ToString('yyyy-MM-dd HH:mm:ss')))."
                break
            }
        }
        Log "Waiting for CSV... ($i/6)"
        Start-Sleep -Seconds 5
    }
    if (-not $csvReady -and (Test-Path $csvPath)) {
        Log "CSV exists but not updated in window; proceeding anyway."
        $csvReady = $true
    }
    if (-not $csvReady) {
        Log "Error: yield_table.csv not found - $csvPath"
        exit 1
    }

    # 2) Git 푸시
    $gitOk = $false
    git status 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Log "오류: 이 폴더는 Git 저장소가 아니거나 git이 PATH에 없습니다."
        exit 1
    }

    git add $csvPath
    $staged = (git diff --cached --name-only 2>&1) -match "yield_table\.csv"
    if (-not $staged) {
        git add --renormalize $csvPath 2>&1 | Out-Null
        $staged = (git diff --cached --name-only 2>&1) -match "yield_table\.csv"
    }
    Log "yield_table.csv staged for commit: $(if ($staged) { 'yes' } else { 'no change' })"

    $today = Get-Date -Format "yyyy-MM-dd"
    $msg = "Update daily CSV $today"
    $commitOut = git commit -m $msg 2>&1
    $commitOut | ForEach-Object { Log $_ }
    $commitSucceeded = ($LASTEXITCODE -eq 0)

    # 커밋 성공 여부와 관계없이 원격에 안 밀린 커밋이 있으면 푸시 시도 (비대화형에서 자격증명 사용)
    $env:GIT_TERMINAL_PROMPT = "0"
    $pushOut = git push 2>&1
    $pushOut | ForEach-Object { Log $_ }
    $pushSucceeded = ($LASTEXITCODE -eq 0)
    if (-not $pushSucceeded) {
        Log "Push failed. Run once in terminal: cd $scriptDir; git push  (log in when prompted, then auto-push may work next time)."
    }

    if ($pushSucceeded) {
        $gitOk = $true
        if (-not $commitSucceeded) {
            Log "No local commit (CSV unchanged vs last commit). Push completed for any existing commits."
            Log "To push current CSV once manually: git add yield_table.csv && git commit -m \"Update daily CSV\" && git push"
        }
    } else {
        if (-not $commitSucceeded) {
            Log "No commit and push failed. Try in terminal: cd $scriptDir; git add yield_table.csv; git commit -m 'Update daily CSV'; git push"
        }
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
