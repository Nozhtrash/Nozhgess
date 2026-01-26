Sub HogarProtegido()
    Dim wsAnexo As Worksheet, wsCarga As Worksheet
    Dim lastRow As Long, filaCarga As Long
    Dim i As Long, fechaActual As Date
    Dim rutCompleto As String, rutSinDV As String, digitoVerificador As String
    Dim fechaInicio As Date, fechaTermino As Date
    
    Set wsAnexo = ThisWorkbook.Sheets("Anexo")
    Set wsCarga = ThisWorkbook.Sheets("Carga")
    
    ' Limpiar hoja Carga antes de llenar
    wsCarga.Cells.Clear
    
    ' Poner encabezados fijos
    wsCarga.Range("A1").Value = "FECHA"
    wsCarga.Range("B1").Value = "RUT"
    wsCarga.Range("C1").Value = "DV"
    wsCarga.Range("D1").Value = "PRESTACIONES"
    wsCarga.Range("E1").Value = "Tipo"
    wsCarga.Range("F1").Value = "PS-FAM"
    wsCarga.Range("G1").Value = "ESPECIALIDAD"
    
    ' Formato texto para columna D (Prestaciones)
    wsCarga.Columns("D").NumberFormat = "@"
    
    filaCarga = 2
    
    ' Última fila con datos en Anexo, columna C (RUT Beneficiario)
    lastRow = wsAnexo.Cells(wsAnexo.Rows.Count, "C").End(xlUp).Row
    
    For i = 11 To lastRow 'Empieza en fila 13 porque ahí empiezan los datos según imagen
        rutCompleto = wsAnexo.Cells(i, "D").Value ' Rut con puntos y guion
        ' Quitar puntos y separar DV
        rutSinDV = Replace(Replace(Split(rutCompleto, "-")(0), ".", ""), ",", "")
        digitoVerificador = Split(rutCompleto, "-")(1)
        
        fechaInicio = wsAnexo.Cells(i, "J").Value ' Fecha Inicio
        fechaTermino = wsAnexo.Cells(i, "K").Value ' Fecha Termino
        
        ' Por cada fecha entre inicio y termino, agregamos una fila
        For fechaActual = fechaInicio To fechaTermino
            wsCarga.Cells(filaCarga, "A").Value = fechaActual
            wsCarga.Cells(filaCarga, "B").Value = rutSinDV
            wsCarga.Cells(filaCarga, "C").Value = digitoVerificador
            wsCarga.Cells(filaCarga, "D").Value = "0203017" ' fijo
            wsCarga.Cells(filaCarga, "E").Value = "PPV"     ' fijo
            wsCarga.Cells(filaCarga, "F").Value = "2295"    ' fijo
            
            filaCarga = filaCarga + 1
        Next fechaActual
    Next i
    
    ' Opcional: ordenar por FECHA ascendente (columna A)
    With wsCarga.Sort
        .SortFields.Clear
        .SortFields.Add Key:=wsCarga.Range("A2:A" & filaCarga - 1), _
            SortOn:=xlSortOnValues, Order:=xlAscending, DataOption:=xlSortNormal
        .SetRange wsCarga.Range("A1:G" & filaCarga - 1)
        .Header = xlYes
        .Apply
    End With
    
    MsgBox "Datos transferidos correctamente a Carga! ??", vbInformation
End Sub