Option Explicit

Sub MarcarRutsConErrores()
    Dim wb As Workbook
    Dim wsList As Worksheet, wsData As Worksheet
    Dim lastList As Long, i As Long
    Dim lastData As Long, r As Long, rr As Long
    Dim dictLines As Object, dictColored As Object
    Dim s As String, num As String
    Dim startPos As Long, endPos As Long
    Dim rutVal As String
    Dim blockStart As Long, blockEnd As Long
    Dim color1 As Long, color2 As Long
    Dim RUTCol As Long, DVCol As Long
    Dim bloquesColoreados As Long

    On Error GoTo ErrHandler
    Set wb = ThisWorkbook
    Set wsList = wb.Worksheets("Rut")               ' Hoja con mensajes "(Linea N) ..."
    Set wsData = wb.Worksheets("HojaPart 001")      ' Hoja a colorear

    ' --- CONFIGURABLES ---
    RUTCol = 2   ' columna B
    DVCol = 3    ' columna C
    color1 = RGB(255, 192, 0)   ' dorado / naranja
    color2 = RGB(0, 176, 240)   ' celeste
    ' ----------------------

    ' crear diccionarios (late binding)
    Set dictLines = CreateObject("Scripting.Dictionary")
    Set dictColored = CreateObject("Scripting.Dictionary")

    ' obtener últimas filas
    lastList = wsList.Cells(wsList.Rows.Count, 1).End(xlUp).Row
    lastData = wsData.Cells(wsData.Rows.Count, RUTCol).End(xlUp).Row
    If lastList = 0 Then
        MsgBox "La hoja 'Rut' está vacía.", vbExclamation
        Exit Sub
    End If

    ' Limpiar colores previos en rango usado (solo columnas RUT/DV)
    wsData.Range(wsData.Cells(1, RUTCol), wsData.Cells(lastData, DVCol)).Interior.Pattern = xlNone

    ' Parsear la hoja "Rut" y extraer números de línea
    For i = 1 To lastList
        s = CStr(wsList.Cells(i, 1).Value)
        If Len(Trim(s)) > 0 Then
            num = ExtractLineNumber(s)
            If num <> "" Then
                If Not dictLines.Exists(CLng(num)) Then dictLines.Add CLng(num), True
            End If
        End If
    Next i

    If dictLines.Count = 0 Then
        MsgBox "No se encontró ninguna línea con formato '(Linea N)' en la hoja 'Rut'.", vbExclamation
        Exit Sub
    End If

    ' Recorrer la hoja de datos de arriba hacia abajo; cuando encontremos una fila
    ' que esté en la lista de líneas de error y no esté ya coloreada, expandir el bloque del RUT y colorear.
    Dim toggleColor As Boolean: toggleColor = True
    bloquesColoreados = 0

    For r = 1 To lastData
        If dictLines.Exists(r) Then
            If Not dictColored.Exists(r) Then
                rutVal = Trim(CStr(wsData.Cells(r, RUTCol).Value))
                If rutVal <> "" Then
                    ' buscar inicio del bloque (mismo RUT hacia arriba)
                    blockStart = r
                    Do While blockStart > 1 And Trim(CStr(wsData.Cells(blockStart - 1, RUTCol).Value)) = rutVal
                        blockStart = blockStart - 1
                    Loop
                    ' buscar fin del bloque (mismo RUT hacia abajo)
                    blockEnd = r
                    Do While blockEnd < lastData And Trim(CStr(wsData.Cells(blockEnd + 1, RUTCol).Value)) = rutVal
                        blockEnd = blockEnd + 1
                    Loop

                    ' elegir color
                    Dim usoColor As Long
                    If toggleColor Then
                        usoColor = color1
                    Else
                        usoColor = color2
                    End If

                    ' colorear todas las filas del bloque (solo columnas RUT y DV)
                    For rr = blockStart To blockEnd
                        wsData.Cells(rr, RUTCol).Interior.Color = usoColor
                        wsData.Cells(rr, DVCol).Interior.Color = usoColor
                        If Not dictColored.Exists(rr) Then dictColored.Add rr, True
                    Next rr

                    toggleColor = Not toggleColor
                    bloquesColoreados = bloquesColoreados + 1
                End If
            End If
        End If
    Next r

    MsgBox "Listo. Se colorearon " & bloquesColoreados & " bloques de RUT con errores.", vbInformation

    Exit Sub

ErrHandler:
    MsgBox "Error: " & Err.Number & " - " & Err.Description, vbCritical

End Sub

' Extrae el primer número que aparece después de "(Linea"
Private Function ExtractLineNumber(txt As String) As String
    Dim pos As Long, k As Long, j As Long, ch As String, num As String
    num = ""
    pos = InStr(1, txt, "(Linea", vbTextCompare)
    If pos = 0 Then
        ' Si no encuentra "(Linea" buscar cualquier número en el texto (caída segura)
        For j = 1 To Len(txt)
            ch = Mid$(txt, j, 1)
            If ch >= "0" And ch <= "9" Then
                num = num & ch
                ' continúa hasta que se termine la secuencia de dígitos
                Dim jj As Long: jj = j + 1
                Do While jj <= Len(txt)
                    ch = Mid$(txt, jj, 1)
                    If ch >= "0" And ch <= "9" Then
                        num = num & ch
                        jj = jj + 1
                    Else
                        Exit Do
                    End If
                Loop
                Exit For
            End If
        Next j
        ExtractLineNumber = num
        Exit Function
    End If

    k = pos + Len("(Linea")
    ' avanzar hasta primer dígito
    Do While k <= Len(txt) And Not (Mid$(txt, k, 1) >= "0" And Mid$(txt, k, 1) <= "9")
        k = k + 1
    Loop
    j = k
    Do While j <= Len(txt) And (Mid$(txt, j, 1) >= "0" And Mid$(txt, j, 1) <= "9")
        num = num & Mid$(txt, j, 1)
        j = j + 1
    Loop
    ExtractLineNumber = num
End Function