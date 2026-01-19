Sub ResaltarPacientesCon13Repeticiones()
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim i As Long
    Dim startRow As Long
    Dim count As Long
    Dim currentRut As String
    Dim nextRut As String
    Dim rng As Range

    ' Establecer la hoja activa
    Set ws = ActiveSheet

    ' Encontrar la última fila con datos en la columna B (RUT)
    lastRow = ws.Cells(ws.Rows.count, "B").End(xlUp).Row

    ' Ordenar la hoja por la columna B (RUT) para agrupar los pacientes
    ' Asumimos que los datos tienen encabezados en la fila 1
    With ws.Sort
        .SortFields.Clear
        .SortFields.Add Key:=ws.Range("B2:B" & lastRow), _
            SortOn:=xlSortOnValues, Order:=xlAscending, DataOption:=xlSortNormal
        .SetRange ws.Range("A1").CurrentRegion
        .Header = xlYes
        .MatchCase = False
        .Orientation = xlTopToBottom
        .SortMethod = xlPinYin
        .Apply
    End With

    ' Iterar a través de las filas para contar grupos y resaltar
    i = 2 ' Comenzar en la fila 2 (asumiendo que la 1 es encabezado)
    
    Do While i <= lastRow
        currentRut = Trim(CStr(ws.Cells(i, 2).Value))
        startRow = i
        count = 0
        
        ' Contar cuántas veces aparece este RUT consecutivamente (ya que está ordenado)
        Do While i <= lastRow
            nextRut = Trim(CStr(ws.Cells(i, 2).Value))
            If nextRut = currentRut Then
                count = count + 1
                i = i + 1
            Else
                Exit Do
            End If
        Loop
        
        ' Si el conteo es exactamente 13, resaltar las filas
        If count = 13 Then
            ' Definir el rango de filas para este grupo
            Set rng = ws.Range(ws.Cells(startRow, 1), ws.Cells(startRow + count - 1, ws.UsedRange.Columns.count))
            
            ' Aplicar formato: Fondo rojo, Letra blanca
            With rng
                .Interior.Color = vbRed
                .Font.Color = vbWhite
            End With
            
            ' REGLA NUEVA:
            ' 1. Limpiar columna K (11) en todas las filas del grupo
            ws.Range(ws.Cells(startRow, 11), ws.Cells(startRow + count - 1, 11)).ClearContents
            
            ' 2. Escribir "D" en columna L (12) SOLO en la primera fila del grupo
            ws.Cells(startRow, 12).Value = "D"
            
            ' 3. Escribir "13 Filas" en columna P (16) SOLO en la primera fila del grupo
            ws.Cells(startRow, 16).Value = "13 Filas"
        End If
    Loop

    MsgBox "Proceso completado. Se han ordenado y marcado los pacientes que se repiten 13 veces.", vbInformation, "Completado"

End Sub


