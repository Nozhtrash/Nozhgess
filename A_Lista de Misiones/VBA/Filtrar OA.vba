Sub FiltrarOA()

    ' =============================================================
    '  FILTRAR OA PERMITIENDO VARIOS CÓDIGOS (separados por coma)
    '  Encabezados esperados:
    '     - Código OA   (o CODIGO OA / CÓDIGO OA)
    '     - Fecha OA
    '     - Folio OA
    ' =============================================================

    Dim inputCodigos As String
    Dim codigosBuscados As Variant

    ' Solicitar códigos separados por coma
    inputCodigos = InputBox( _
        "Ingresa uno o varios CÓDIGOS OA separados por coma:" & vbCrLf & _
        "Ej: 2505876, 2504092, 9001043", _
        "Filtrar OA")

    If Trim(inputCodigos) = "" Then Exit Sub

    codigosBuscados = Split(inputCodigos, ",")

    Dim sh As Worksheet
    Set sh = ActiveSheet

    Dim lastRow As Long
    lastRow = sh.Cells(sh.Rows.Count, "A").End(xlUp).Row

    Dim colCod As Long, colFecha As Long, colFolio As Long

    ' =============================================================
    '  DETECTAR COLUMNAS POR ENCABEZADO (fila 1)
    ' =============================================================
    Dim c As Range, titulo As String
    For Each c In sh.Rows(1).Cells
        titulo = Trim(UCase(c.Value))

        Select Case titulo
            Case "CODIGO OA", "CÓDIGO OA"
                colCod = c.Column
            Case "FECHA OA"
                colFecha = c.Column
            Case "FOLIO OA"
                colFolio = c.Column
        End Select
    Next c

    If colCod = 0 Or colFecha = 0 Or colFolio = 0 Then
        MsgBox "No encontré las columnas 'Código OA', 'Fecha OA' y/o 'Folio OA'.", vbCritical
        Exit Sub
    End If

    ' =============================================================
    '  PROCESAR FILA POR FILA
    ' =============================================================
    Dim i As Long
    For i = 2 To lastRow

        Dim codigos As Variant, fechas As Variant, folios As Variant
        Dim newCod As String, newFecha As String, newFolio As String
        newCod = "": newFecha = "": newFolio = ""

        ' Convertir contenido a texto exacto antes del Split
        codigos = Split(CStr(sh.Cells(i, colCod).Text), " | ")
        fechas = Split(CStr(sh.Cells(i, colFecha).Text), " | ")
        folios = Split(CStr(sh.Cells(i, colFolio).Text), " | ")

        Dim j As Long, k As Long

        ' Recorrer cada código de la fila
        For j = LBound(codigos) To UBound(codigos)

            ' Comparar contra todos los códigos buscados
            For k = LBound(codigosBuscados) To UBound(codigosBuscados)

                If Trim(codigos(j)) = Trim(codigosBuscados(k)) Then

                    If newCod = "" Then
                        newCod = Trim(codigos(j))
                        newFecha = Trim(fechas(j))
                        newFolio = Trim(folios(j))
                    Else
                        newCod = newCod & " | " & Trim(codigos(j))
                        newFecha = newFecha & " | " & Trim(fechas(j))
                        newFolio = newFolio & " | " & Trim(folios(j))
                    End If

                    Exit For ' ya coincidió → pasar al siguiente j
                End If

            Next k

        Next j

        ' Escribir resultados
        sh.Cells(i, colCod).Value = newCod
        sh.Cells(i, colFecha).Value = newFecha
        sh.Cells(i, colFolio).Value = newFolio

    Next i

    MsgBox "Filtrado de OA completado.", vbInformation

End Sub