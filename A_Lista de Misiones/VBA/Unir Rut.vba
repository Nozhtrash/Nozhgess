Sub UnirRUTyDV()
    ' Declaramos las variables, para que esto sea serio y ordenado.
    Dim UltimaFila As Long
    Dim i As Long

    ' Encontramos la última fila con datos en la columna B, no queremos irnos al infinito y más allá.
    UltimaFila = Cells(Rows.Count, "B").End(xlUp).Row

    ' Recorremos cada fila desde la segunda (la primera suele ser el encabezado, ¿verdad?)
    For i = 2 To UltimaFila
        ' Si la celda en la columna B tiene algo y la celda en la columna C también, ¡a unir se ha dicho!
        If Not IsEmpty(Cells(i, "B").Value) And Not IsEmpty(Cells(i, "C").Value) Then
            ' Concatenamos el valor de la columna B, un guion, y el valor de la columna C.
            ' Lo guardamos en la misma columna B, ¡optimización a tope!
            Cells(i, "B").Value = Cells(i, "B").Value & "-" & Cells(i, "C").Value
            ' Borramos el contenido de la columna C, porque ya no lo necesitamos. ¡Adiós, columna C! 👋
            Cells(i, "C").ClearContents
        End If
    Next i

    ' Un mensaje para que sepas que la magia ha ocurrido.
    MsgBox "¡Columnas B y C unidas con éxito en la columna B! La columna C ha sido limpiada.", vbInformation, "Misión Cumplida, Nozh"

End Sub