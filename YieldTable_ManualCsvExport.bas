' ============================================================
' yield_table 를 UTF-8 CSV 로 저장 (버튼으로 수동 실행)
' - 통합문서를 열 때 자동 실행 없음
' - 값 로드 확인 후, 개발자가 추가한 [양식 컨트롤] 버튼에 이 매크로 연결
' ============================================================
' 주의: .xlsx 에는 VBA 를 넣을 수 없음
'       한 번 [다른 이름으로 저장] > "Excel 매크로 사용 통합문서(*.xlsm)" 로 저장하세요.
' ============================================================
' 버튼 연결: 개발자 도구 > 삽입 > 단추(양식 컨트롤) > 시트에 그린 뒤
'           매크로 지정에서 "SaveYieldTableAsCsvUtf8" 선택
' ============================================================

Option Explicit

' 내보낼 시트 (1 = 첫 번째 시트)
Private Const EXPORT_SHEET_INDEX As Long = 1

' CSV 저장 경로 (통합문서와 같은 폴더의 yield_table.csv)
' 고정 경로를 쓰려면 USE_FIXED_PATH = True 로 바꾸세요.
Private Const USE_FIXED_PATH As Boolean = False
Private Const FIXED_CSV_PATH As String = "C:\Users\infomax\Documents\Cursor\yield_table.csv"

' 버튼에 연결할 공개 매크로
Public Sub SaveYieldTableAsCsvUtf8()
    Dim wsSource As Worksheet
    Dim wbTemp As Workbook
    Dim csvPath As String

    Set wbTemp = Nothing
    On Error GoTo ErrHandle

    If ThisWorkbook.Worksheets.Count < EXPORT_SHEET_INDEX Then
        MsgBox "시트가 없습니다.", vbExclamation
        Exit Sub
    End If

    Set wsSource = ThisWorkbook.Worksheets(EXPORT_SHEET_INDEX)

    If USE_FIXED_PATH Then
        csvPath = FIXED_CSV_PATH
    Else
        csvPath = QualifyPath(ThisWorkbook.Path) & "yield_table.csv"
    End If

    Application.ScreenUpdating = False
    Application.DisplayAlerts = False

    ' 원본은 건드리지 않고, 시트 복사 → 임시 통합문서만 CSV 로 저장
    wsSource.Copy
    Set wbTemp = ActiveWorkbook

    On Error Resume Next
    wbTemp.SaveAs Filename:=csvPath, FileFormat:=62, CreateBackup:=False
    If Err.Number <> 0 Then
        Err.Clear
        wbTemp.SaveAs Filename:=csvPath, FileFormat:=xlCSV, CreateBackup:=False
    End If
    On Error GoTo ErrHandle

    wbTemp.Close SaveChanges:=False

    Application.DisplayAlerts = True
    Application.ScreenUpdating = True

    MsgBox "CSV 저장 완료" & vbCrLf & csvPath, vbInformation
    Exit Sub

ErrHandle:
    Application.DisplayAlerts = True
    Application.ScreenUpdating = True
    On Error Resume Next
    If Not wbTemp Is Nothing Then wbTemp.Close SaveChanges:=False
    On Error GoTo 0
    MsgBox "저장 실패: " & Err.Description, vbCritical
End Sub

Private Function QualifyPath(ByVal p As String) As String
    If Len(p) = 0 Then QualifyPath = vbNullString: Exit Function
    If Right$(p, 1) = "\" Then QualifyPath = p Else QualifyPath = p & "\"
End Function
