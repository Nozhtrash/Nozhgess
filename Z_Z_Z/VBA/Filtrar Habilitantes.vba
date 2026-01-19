Sub FiltrarHabilitantes()

    ' =============================================================
    '  FILTRAR HABILITANTES PERMITIENDO VARIOS CÓDIGOS
    '  Encabezados esperados:
    '     - C Hab
    '     - F Hab
    ' =============================================================

    Dim inputCodigos As String
    Dim codigosBuscados As Variant

    inputCodigos = InputBox( _
        "Ingresa uno o varios CÓDIGOS HABILITANTES separados por coma:" & vbCrLf & _
        "Ej: 0305091, 9001043", _
        "Filtrar Habilitantes")

    If Trim(inputCodigos) = "" Then Exit Sub

    codigosBuscados = Split(inputCodigos, ",")

    Dim sh As Worksheet
    Set sh = ActiveSheet

    Dim lastRow As Long
    lastRow = sh.Cells(sh.Rows.Count, "A").End(xlUp).Row

    Dim colCod As Long, colFecha As Long

    ' =============================================================
    '  DETECTAR COLUMNAS POR ENCABEZADO
    ' =============================================================
    Dim c As Range, titulo As String
    For Each c In sh.Rows(1).Cells

        titulo = Trim(UCase(c.Value))

        Select Case titulo
            Case "C HAB"
                colCod = c.Column
            Case "F HAB"
                colFecha = c.Column
        End Select

    Next c

    If colCod = 0 Or colFecha = 0 Then
        MsgBox "No encontré las columnas 'C Hab' y/o 'F Hab'.", vbCritical
        Exit Sub
    End If

    ' =============================================================
    '  PROCESAR FILAS
    ' =============================================================
    Dim i As Long
    For i = 2 To lastRow

        Dim codigos As Variant, fechas As Variant
        Dim newCod As String, newFecha As String
        newCod = "": newFecha = ""

        ' Convertir a texto exacto antes de Split
        codigos = Split(CStr(sh.Cells(i, colCod).Text), " | ")
        fechas = Split(CStr(sh.Cells(i, colFecha).Text), " | ")

        Dim j As Long, k As Long

        For j = LBound(codigos) To UBound(codigos)

            For k = LBound(codigosBuscados) To UBound(codigosBuscados)

                If Trim(codigos(j)) = Trim(codigosBuscados(k)) Then

                    If newCod = "" Then
                        newCod = Trim(codigos(j))
                        newFecha = Trim(fechas(j))
                    Else
                        newCod = newCod & " | " & Trim(codigos(j))
                        newFecha = newFecha & " | " & Trim(fechas(j))
                    End If

                    Exit For
                End If

            Next k

        Next j

        sh.Cells(i, colCod).Value = newCod
        sh.Cells(i, colFecha).Value = newFecha

    Next i

    MsgBox "Filtrado de habilitantes completado.", vbInformation

End Sub