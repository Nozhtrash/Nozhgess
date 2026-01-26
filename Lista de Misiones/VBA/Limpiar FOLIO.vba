Sub LimpiarColumnaS_codigos()

    Dim rng As Range
    Dim celda As Range
    Dim partes As Variant
    Dim bloque As Variant
    Dim nuevoTexto As String
    Dim codigo As String
    Dim i As Long
    
    ' Define el rango en columna S con datos
    Set rng = Range("S2:S" & Cells(Rows.Count, "S").End(xlUp).Row)

    For Each celda In rng
        If Trim(celda.Value) <> "" Then
            
            partes = Split(celda.Value, " | ")
            nuevoTexto = ""
            
            For i = LBound(partes) To UBound(partes)
                
                bloque = partes(i)
                
                ' Extraer código
                codigo = Trim(Split(Split(bloque, "Cód")(1), "/")(0))
                
                ' Si el código es uno de los permitidos, lo dejamos
                If codigo = "0305090" Or codigo = "9001043" Then
                    If nuevoTexto = "" Then
                        nuevoTexto = bloque
                    Else
                        nuevoTexto = nuevoTexto & " | " & bloque
                    End If
                End If
                
            Next i
            
            celda.Value = nuevoTexto
        
        End If
    Next celda
    
    MsgBox "Limpieza completada ✔", vbInformation
    
End Sub