# yield_table.xlsm을 "사용자가 연 것처럼" 실행 → 엑셀 내 매크로가 새로고침 후 CSV 저장
# 사용 전: yield_table.xlsx를 .xlsm으로 저장하고, 아래 VBA(Open_Workbook_Macro.txt)를 ThisWorkbook에 넣어 두세요.

$excelPath = "C:\Users\infomax\Documents\Cursor\yield_table.xlsm"   # 매크로 포함 파일(.xlsm)

if (-not (Test-Path $excelPath)) {
    Write-Host "파일이 없습니다: $excelPath"
    Write-Host "yield_table.xlsx를 yield_table.xlsm으로 저장하고 매크로를 넣은 뒤 다시 실행하세요."
    exit 1
}

$p = Start-Process -FilePath $excelPath -PassThru -Wait
Write-Host "엑셀 매크로 완료(종료코드: $($p.ExitCode))."
