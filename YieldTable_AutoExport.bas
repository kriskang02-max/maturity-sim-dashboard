' ============================================================
' 표준 모듈로 삽입: VBA 편집기 > 삽입 > 모듈
' ThisWorkbook.Workbook_Open 에서:
'   ExportYieldTableToCsvAndQuit
' 한 줄만 호출하면 됩니다.
' ============================================================

Option Explicit

' CSV 저장 경로: 통상 통합문서 폴더. 고정 경로를 쓰려면 USE_FIXED_CSV_PATH = True 로 바꾸세요.
Private Const USE_FIXED_CSV_PATH As Boolean = False
Private Const FIXED_CSV_PATH As String = "C:\Users\infomax\Documents\Cursor\yield_table.csv"

Private Const TARGET_SHEET_INDEX As Long = 1
Private Const HEADER_SCAN_MAX_ROW As Long = 20
Private Const HEADER_TEXT_HINT As String = "날짜"
Private Const DATA_START_FALLBACK_ROW As Long = 2
Private Const DATA_SEARCH_MAX_ROW As Long = 500

Private Const LOAD_TIMEOUT_SECONDS As Long = 300
Private Const LOAD_MIN_WAIT_SECONDS As Long = 20

' ----------------------------------------------------------------
Public Sub ExportYieldTableToCsvAndQuit()
    Dim ws As Worksheet
    Dim csvPath As String
    Dim firstDateCol As Long
    Dim dataStartRow As Long

    On Error GoTo ErrHandle

    Set ws = ThisWorkbook.Worksheets(TARGET_SHEET_INDEX)

    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = False
    Application.DisplayAlerts = False
    Application.EnableEvents = False

    DisableBackgroundRefresh

    firstDateCol = FindHeaderColumnContaining(ws, HEADER_SCAN_MAX_ROW, HEADER_TEXT_HINT)
    If firstDateCol < 1 Then firstDateCol = 5

    dataStartRow = FindFirstNonEmptyInColumn(ws, firstDateCol, DATA_START_FALLBACK_ROW, DATA_SEARCH_MAX_ROW)
    If dataStartRow < 1 Then dataStartRow = DATA_START_FALLBACK_ROW

    WaitForSheetToLoad ws, firstDateCol, dataStartRow, LOAD_TIMEOUT_SECONDS, LOAD_MIN_WAIT_SECONDS

    If USE_FIXED_CSV_PATH Then
        csvPath = FIXED_CSV_PATH
    Else
        csvPath = QualifyPath(ThisWorkbook.Path) & "yield_table.csv"
    End If

    SaveThisWorkbookAsUtf8Csv csvPath

    ThisWorkbook.Saved = True
    Application.ScreenUpdating = True
    Application.EnableEvents = True
    Application.DisplayAlerts = False
    Application.Quit
    Exit Sub

ErrHandle:
    Application.ScreenUpdating = True
    Application.EnableEvents = True
    Application.DisplayAlerts = True
    MsgBox "ExportYieldTableToCsv 오류: " & Err.Description, vbCritical
End Sub

' ----------------------------------------------------------------
Private Sub DisableBackgroundRefresh()
    Dim conn As WorkbookConnection
    Dim ws As Worksheet
    Dim qt As QueryTable
    Dim lo As ListObject

    On Error Resume Next
    For Each conn In ThisWorkbook.Connections
        conn.OLEDBConnection.BackgroundQuery = False
        conn.ODBCConnection.BackgroundQuery = False
    Next conn

    For Each ws In ThisWorkbook.Worksheets
        For Each qt In ws.QueryTables
            qt.BackgroundQuery = False
        Next qt
        For Each lo In ws.ListObjects
            lo.QueryTable.BackgroundQuery = False
        Next lo
    Next ws
    On Error GoTo 0
End Sub

' ExportMarketDbLong 과 유사하되, 날짜/금리가 전부 0 인 '로딩 전' 상태는 완료로 보지 않음
Private Sub WaitForSheetToLoad(ByVal ws As Worksheet, ByVal firstDateCol As Long, ByVal dataStartRow As Long, _
    ByVal timeoutSeconds As Long, ByVal minWaitSeconds As Long)

    Dim t0 As Single, lastChange As Single
    Dim prevSig As String, sig As String
    Dim lastCol As Long

    t0 = Timer
    lastChange = Timer
    prevSig = vbNullString

    On Error Resume Next

    Application.Calculation = xlCalculationAutomatic

    ThisWorkbook.RefreshAll
    Application.CalculateFullRebuild
    Application.CalculateUntilAsyncQueriesDone

    lastCol = ws.Cells(dataStartRow, ws.Columns.Count).End(xlToLeft).Column
    If lastCol < firstDateCol + 1 Then lastCol = firstDateCol + 20

    Do
        DoEvents

        sig = CStr(ws.Cells(dataStartRow, firstDateCol).Text) & "|" & _
              CStr(ws.Cells(dataStartRow, firstDateCol + 1).Text) & "|" & _
              CStr(ws.Cells(dataStartRow + 1, firstDateCol + 1).Text)

        If sig <> prevSig Then
            prevSig = sig
            lastChange = Timer
        End If

        If (Timer - t0) >= minWaitSeconds Then
            If Application.CalculationState = xlDone And Not AnyConnectionsRefreshing() Then
                If (Timer - lastChange) >= 3 Then
                    ' "0" 만 찬 상태(스크린샷)는 아직 로드 안 된 것으로 간주
                    If RowLooksLikeRealMarketData(ws, dataStartRow, firstDateCol, lastCol) Then
                        Exit Do
                    End If
                End If
            End If
        End If

        If (Timer - t0) >= timeoutSeconds Then Exit Do
    Loop

    On Error GoTo 0
End Sub

' 첫 데이터 행: 날짜가 YYYYMMDD 처럼 보이고, 금리 열 중 하나라도 0 초과
Private Function RowLooksLikeRealMarketData(ByVal ws As Worksheet, ByVal r As Long, ByVal dateCol As Long, ByVal lastCol As Long) As Boolean
    Dim v As Variant
    Dim d As Double
    Dim c As Long
    Dim endCol As Long
    Dim s As String

    RowLooksLikeRealMarketData = False

    v = ws.Cells(r, dateCol).Value
    If IsError(v) Or IsEmpty(v) Then Exit Function
    s = Trim$(CStr(v))
    If Len(s) = 0 Then Exit Function
    If s = "0" Then Exit Function

    If IsNumeric(v) Then
        d = CDbl(v)
        If d <= 0 Then Exit Function
        If d >= 20000101# And d <= 20991231# Then
            GoTo CheckYields
        End If
    End If
    If IsDate(v) Then GoTo CheckYields
    Exit Function

CheckYields:
    endCol = dateCol + 18
    If endCol > lastCol Then endCol = lastCol
    For c = dateCol + 1 To endCol
        v = ws.Cells(r, c).Value
        If Not IsError(v) And IsNumeric(v) Then
            If CDbl(v) > 0.0000001 Then
                RowLooksLikeRealMarketData = True
                Exit Function
            End If
        End If
    Next c
End Function

Private Function AnyConnectionsRefreshing() As Boolean
    Dim c As WorkbookConnection
    On Error Resume Next
    AnyConnectionsRefreshing = False
    For Each c In ThisWorkbook.Connections
        If Not c Is Nothing Then
            If c.Refreshing Then
                AnyConnectionsRefreshing = True
                Exit Function
            End If
        End If
    Next c
    On Error GoTo 0
End Function

Private Sub SaveThisWorkbookAsUtf8Csv(ByVal csvPath As String)
    ' CSV 저장 시 통상 활성 시트만 저장되므로 대상 시트를 활성화
    ThisWorkbook.Worksheets(TARGET_SHEET_INDEX).Activate
    On Error Resume Next
    ThisWorkbook.SaveAs Filename:=csvPath, FileFormat:=62, CreateBackup:=False
    If Err.Number <> 0 Then
        Err.Clear
        ThisWorkbook.SaveAs Filename:=csvPath, FileFormat:=xlCSV, CreateBackup:=False
    End If
    On Error GoTo 0
End Sub

' ----------------------------------------------------------------
Private Function QualifyPath(ByVal p As String) As String
    If Len(p) = 0 Then QualifyPath = vbNullString: Exit Function
    If Right$(p, 1) = "\" Then QualifyPath = p Else QualifyPath = p & "\"
End Function

Private Function FindHeaderColumnContaining(ByVal ws As Worksheet, ByVal maxHeaderRow As Long, ByVal hint As String) As Long
    Dim rr As Long, cc As Long
    Dim lastCol As Long
    Dim v As Variant
    Dim s As String

    FindHeaderColumnContaining = -1
    lastCol = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    If lastCol < 1 Then lastCol = 200

    For rr = 1 To maxHeaderRow
        For cc = 1 To lastCol
            v = ws.Cells(rr, cc).Value
            If Not IsError(v) Then
                s = Trim$(CStr(v))
                If Len(s) > 0 Then
                    If InStr(1, s, hint, vbTextCompare) > 0 Then
                        FindHeaderColumnContaining = cc
                        Exit Function
                    End If
                End If
            End If
        Next cc
    Next rr
End Function

Private Function FindFirstNonEmptyInColumn(ByVal ws As Worksheet, ByVal colIndex As Long, ByVal startRow As Long, ByVal maxRow As Long) As Long
    Dim r As Long
    Dim v As Variant
    Dim s As String
    For r = startRow To maxRow
        v = ws.Cells(r, colIndex).Value
        If Not IsError(v) Then
            s = Trim$(CStr(v))
            ' 로딩 전 플레이스홀더 0 은 제외
            If Len(s) > 0 And s <> "0" Then
                FindFirstNonEmptyInColumn = r
                Exit Function
            End If
        End If
    Next r
    FindFirstNonEmptyInColumn = -1
End Function
