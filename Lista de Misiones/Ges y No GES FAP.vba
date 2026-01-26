Sub GESoNoGESGASTROParaFAPS()
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim i As Long
    Dim valorL As Long
    Dim edad As Integer
    
    ' Establece la hoja de trabajo "NOMBRE"
    Set ws = ThisWorkbook.Sheets("Matías")
    
    ' Encuentra la última fila con datos en la columna K
    lastRow = ws.Cells(ws.Rows.Count, "K").End(xlUp).Row
    
    ' Recorre todas las filas desde la 2 hasta la última
    For i = 2 To lastRow
        valorK = ws.Cells(i, "K").Value
        edad = ws.Cells(i, "E").Value
        
        ' Verifica si el valor en la columna K es uno de los números requeridos
        If valorK = 1802028 Or valorK = 1802029 Or valorK = 1802081 Then
            ' Verifica las condiciones de la columna E y asigna NG o GES en la columna O
            If edad < 35 Or edad > 49 Then
                ws.Cells(i, "P").Value = "NG"
            ElseIf edad >= 35 And edad <= 49 Then
                ws.Cells(i, "P").Value = "GES"
                End If
        End If
        
    Next i
    MsgBox "Se han Marcado los Pacientes con Éxito :D By:ElMati"
End Sub