Sub SepararRUTyDV()
    Dim ultimaFila As Long
    Dim i As Long
    Dim rut As String
    Dim posicionGuion As Integer
    Dim posicionEspacio As Integer

    ' Encontrar la última fila con datos en la columna B
    ultimaFila = Cells(Rows.Count, 2).End(xlUp).Row

    ' Recorrer las filas desde la 1 hasta la última con datos
    For i = 1 To ultimaFila
        rut = Cells(i, 2).Value ' Leer el RUT de la columna B

        ' Buscar la posición del guion en el RUT
        posicionGuion = InStr(rut, "-")
        ' Buscar la posición del espacio en el RUT
        posicionEspacio = InStr(rut, " ")
       
        ' Verificar si hay un guion o espacio en el RUT
        If posicionGuion > 0 Then
            ' Separar usando el guion
            Cells(i, 2).Value = Left(rut, posicionGuion - 1)
            Cells(i, 3).Value = Mid(rut, posicionGuion + 1, Len(rut) - posicionGuion)
        ElseIf posicionEspacio > 0 Then
            ' Separar usando el espacio
            Cells(i, 2).Value = Left(rut, posicionEspacio - 1)
            Cells(i, 3).Value = Mid(rut, posicionEspacio + 1, Len(rut) - posicionEspacio)
        End If
    Next i
    MsgBox "Se ha separado el RUT y DV correctamente :D By:ElMati"
End Sub