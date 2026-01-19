Sub Paso2CombinarFechas()

    Dim ws As Worksheet
    Set ws = ThisWorkbook.Worksheets("Resumen")

    Dim sets As Variant
    sets = Array( _
        Array("C", "D", "E"), _
        Array("G", "H", "I"), _
        Array("K", "L", "M"), _
        Array("O", "P", "Q"), _
        Array("S", "T", "U"), _
        Array("W", "X", "Y"), _
        Array("AA", "AB", "AC"), _
        Array("AE", "AF", "AG"), _
        Array("AI", "AJ", "AK"), _
        Array("AM", "AN", "AO"), _
        Array("AQ", "AR", "AS") _
    )

    Dim lastRow As Long
    lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row

    Dim trio As Variant
    Dim r As Long

    ' Procesamos en orden inverso para evitar que las columnas eliminadas alteren las posiciones de las siguientes
    Dim i As Long
    For i = UBound(sets) To LBound(sets) Step -1
        trio = sets(i)
        Dim colD As Long, colM As Long, colY As Long
        colD = ws.Range(trio(0) & "1").Column
        colM = ws.Range(trio(1) & "1").Column
        colY = ws.Range(trio(2) & "1").Column

        For r = 2 To lastRow
            Dim d, m, y
            d = ws.Cells(r, colD).Value
            m = ws.Cells(r, colM).Value
            y = ws.Cells(r, colY).Value

            If IsEmpty(d) And IsEmpty(m) And IsEmpty(y) Then
                ws.Cells(r, colD).Value = ""
            Else
                On Error Resume Next
                ws.Cells(r, colD).Value = DateSerial(CInt(y), CInt(m), CInt(d))
                ws.Cells(r, colD).NumberFormat = "dd/mm/yyyy"
                On Error GoTo 0
            End If
        Next r

        ' Eliminar columnas de Mes y Año (en orden inverso para que no se desplacen)
        ws.Columns(colY).Delete
        ws.Columns(colM).Delete
    Next i

    MsgBox "? Fechas combinadas y columnas eliminadas con éxito, By:Nozh", vbInformation

End Sub

