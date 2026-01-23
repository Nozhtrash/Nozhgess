Option Explicit

' Versión corregida y más robusta:
' Divide Hoja1 en partes de 500 filas de datos (cada hoja tendrá encabezado + hasta 500 filas)
' Corta los bloques de abajo hacia arriba para evitar cambios de índices que rompan el bucle.
Sub SplitSheet500_CutPaste_Fixed()
    Dim wb As Workbook: Set wb = ThisWorkbook
    Dim src As Worksheet
    Dim headerRow As Long: headerRow = 1
    Dim lastCol As Long, lastRow As Long, totalRows As Long, parts As Long
    Dim i As Long, startRow As Long, endRow As Long
    Dim newS As Worksheet
    Dim baseName As String: baseName = "HojaPart"
    Dim sheetName As String
    
    On Error GoTo ErrHandler
    Application.ScreenUpdating = False
    Application.EnableEvents = False
    Application.Calculation = xlCalculationManual

    ' Ajusta el nombre si tu hoja se llama distinto
    Set src = wb.Worksheets("Hoja1")

    ' Última columna usada en el encabezado
    lastCol = src.Cells(headerRow, src.Columns.Count).End(xlToLeft).Column
    ' Última fila con datos (columna A)
    lastRow = src.Cells(src.Rows.Count, 1).End(xlUp).Row
    totalRows = lastRow - headerRow
    If totalRows <= 0 Then
        MsgBox "No hay filas de datos debajo del encabezado.", vbInformation
        GoTo Cleanup
    End If

    ' Cuántas partes necesitamos (500 por hoja)
    parts = (totalRows + 499) \ 500  ' división entera redondeando hacia arriba

    ' Cortamos de abajo hacia arriba para no romper índices
    For i = parts To 1 Step -1
        startRow = headerRow + 1 + (i - 1) * 500
        endRow = Application.WorksheetFunction.Min(headerRow + i * 500, lastRow)
        If startRow > endRow Then GoTo NextPart

        ' Nombre con ceros (opcional): HojaPart 001, 002...
        sheetName = baseName & " " & Format(i, "000")
        sheetName = GetAvailableSheetName(wb, sheetName)

        Set newS = wb.Worksheets.Add(After:=wb.Sheets(wb.Sheets.Count))
        newS.Name = sheetName

        ' Copiar encabezado
        src.Range(src.Cells(headerRow, 1), src.Cells(headerRow, lastCol)).Copy Destination:=newS.Cells(headerRow, 1)

        ' Cortar el bloque de filas (startRow : endRow) y pegar en la nueva hoja en fila 2
        src.Range(src.Rows(startRow), src.Rows(endRow)).Cut Destination:=newS.Cells(headerRow + 1, 1)
NextPart:
    Next i

    MsgBox "Listo. Se crearon " & parts & " hoja(s).", vbInformation

Cleanup:
    Application.CutCopyMode = False
    Application.ScreenUpdating = True
    Application.EnableEvents = True
    Application.Calculation = xlCalculationAutomatic
    Exit Sub

ErrHandler:
    MsgBox "Error " & Err.Number & ": " & Err.Description, vbCritical
    Resume Cleanup
End Sub

' Devuelve un nombre de hoja único (evita colisiones)
Private Function GetAvailableSheetName(wb As Workbook, desired As String) As String
    Dim candidate As String
    Dim i As Long: i = 1
    candidate = Left(desired, 31) ' límite 31 caracteres para nombres de hoja
    Do While SheetExists(wb, candidate)
        candidate = Left(desired, 25) & " (" & i & ")"
        i = i + 1
    Loop
    GetAvailableSheetName = candidate
End Function

' Comprueba si existe una hoja con ese nombre
Private Function SheetExists(wb As Workbook, shName As String) As Boolean
    On Error Resume Next
    Dim sht As Worksheet
    Set sht = wb.Worksheets(shName)
    SheetExists = Not (sht Is Nothing)
    On Error GoTo 0
End Function