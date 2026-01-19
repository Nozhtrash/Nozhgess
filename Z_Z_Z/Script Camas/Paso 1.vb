Sub Paso1CopiarColumnasAResumen()

    Dim wsOrigen As Worksheet
    Dim wsResumen As Worksheet
    Dim lastRow As Long
    
    Set wsOrigen = ThisWorkbook.Sheets("General")
    Set wsResumen = ThisWorkbook.Sheets("Resumen")
    
    ' Limpiar hoja Resumen antes de pegar
    wsResumen.Cells.ClearContents
    
    ' Determinar última fila basada en la columna L (RUT)
    lastRow = wsOrigen.Cells(wsOrigen.Rows.Count, "L").End(xlUp).Row

    ' Copiar columnas manualmente y con precisión quirúrgica 🧠🔪

    ' RUT, DV y Ficha
    wsOrigen.Range("L1:L" & lastRow).Copy wsResumen.Range("A1") ' RUT
    wsOrigen.Range("M1:M" & lastRow).Copy wsResumen.Range("B1") ' DV
    wsOrigen.Range("F1:F" & lastRow).Copy wsResumen.Range("AV1") ' Ficha

    ' Ingreso
    wsOrigen.Range("AU1:AX" & lastRow).Copy wsResumen.Range("C1") ' Día, Mes, Año, Área ingreso

    ' Traslados 1 al 9
    Dim colBase As Variant, destinoCol As String
    colBase = Array("AY", "AZ", "BA", "BB", _
                    "BC", "BD", "BE", "BF", _
                    "BG", "BH", "BI", "BJ", _
                    "BK", "BL", "BM", "BN", _
                    "BO", "BP", "BQ", "BR", _
                    "BS", "BT", "BU", "BV", _
                    "BW", "BX", "BY", "BZ", _
                    "CA", "CB", "CC", "CD", _
                    "CE", "CF", "CG", "CH")
                    
    destinoCol = "G" ' Comenzamos a copiar traslados en la columna G (col 7)

    Dim i As Long
    For i = 0 To UBound(colBase)
        wsOrigen.Range(colBase(i) & "1:" & colBase(i) & lastRow).Copy wsResumen.Cells(1, 7 + i)
    Next i

    ' Egreso
    wsOrigen.Range("CK1:CN" & lastRow).Copy wsResumen.Cells(1, 43) ' AQ = Col 43

    ' Días Estadía
    wsOrigen.Range("CO1:CO" & lastRow).Copy wsResumen.Cells(1, 47) ' AU = Col 47

    MsgBox "? Copia de columnas completada correctamente en la hoja 'Resumen'.", vbInformation

End Sub


