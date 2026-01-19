Sub Paso3CargaMasiva()

    Dim wsResumen As Worksheet, wsCarga As Worksheet
    Dim i As Long, lastRow As Long, outputRow As Long
    Dim rut As String, dv As String
    Dim fechaInicio As Date, fechaFin As Date
    Dim camas(0 To 9) As String
    Dim fechas(0 To 9) As Date
    Dim fechaEgreso As Date
    Dim j As Long, k As Long

    Dim codigoCama As String
    Dim codigoExtra As String

    ' Diccionarios de códigos
    Dim dictCamas As Object, dictCodigosExtra As Object
    Set dictCamas = CreateObject("Scripting.Dictionary")
    Set dictCodigosExtra = CreateObject("Scripting.Dictionary")

    ' Mapear camas a códigos
    dictCamas.Add "404", "0203105"
    dictCamas.Add "405", "0203002"
    dictCamas.Add "406", "0203005"
    dictCamas.Add "411", "0203003"
    dictCamas.Add "412", "0203006"
    dictCamas.Add "414", "0203004"
    dictCamas.Add "415", "0203007"

    ' Mapear códigos a códigos extra (F)
    dictCodigosExtra.Add "0203105", "2285"
    dictCodigosExtra.Add "0203002", "2279"
    dictCodigosExtra.Add "0203005", "2282"
    dictCodigosExtra.Add "0203003", "2280"
    dictCodigosExtra.Add "0203006", "2283"
    dictCodigosExtra.Add "0203004", "2281"
    dictCodigosExtra.Add "0203007", "2284"

    Set wsResumen = ThisWorkbook.Sheets("Resumen")
    Set wsCarga = ThisWorkbook.Sheets("Carga Masiva")

    lastRow = wsResumen.Cells(wsResumen.Rows.Count, "A").End(xlUp).Row
    outputRow = wsCarga.Cells(wsCarga.Rows.Count, "B").End(xlUp).Row + 1

    For i = 2 To lastRow
        rut = wsResumen.Cells(i, "A").Value
        dv = wsResumen.Cells(i, "B").Value

        fechas(0) = wsResumen.Cells(i, "C").Value
        camas(0) = wsResumen.Cells(i, "D").Value

        For j = 1 To 9
            If IsDate(wsResumen.Cells(i, 4 + (j * 2) - 1).Value) Then
                fechas(j) = wsResumen.Cells(i, 4 + (j * 2) - 1).Value
                camas(j) = wsResumen.Cells(i, 4 + (j * 2)).Value
            Else
                Exit For
            End If
        Next j

        Dim totalEtapas As Long
        totalEtapas = j

        fechaEgreso = wsResumen.Cells(i, "W").Value

        For k = 0 To totalEtapas - 1
            If k < totalEtapas - 1 Then
                fechaFin = DateAdd("d", -1, fechas(k + 1))
            Else
                fechaFin = fechaEgreso
            End If

            Dim fechaActual As Date
            For fechaActual = fechas(k) To fechaFin
                wsCarga.Cells(outputRow, "B").Value = rut
                wsCarga.Cells(outputRow, "C").Value = dv
                wsCarga.Cells(outputRow, "A").Value = fechaActual

                ' Ver si la cama tiene código
                If dictCamas.exists(camas(k)) Then
                    codigoCama = dictCamas(camas(k))
                    wsCarga.Cells(outputRow, "D").Value = codigoCama

                    ' Agregar código extra si corresponde
                    If dictCodigosExtra.exists(codigoCama) Then
                        wsCarga.Cells(outputRow, "F").Value = dictCodigosExtra(codigoCama)
                    End If
                Else
                    ' Si no tiene código, dejar cama original
                    wsCarga.Cells(outputRow, "D").Value = camas(k)
                    wsCarga.Cells(outputRow, "F").ClearContents
                End If

                wsCarga.Cells(outputRow, "E").Value = "PPV"
                outputRow = outputRow + 1
            Next fechaActual
        Next k

    Next i

    MsgBox "Carga completada con éxito. ¡Todos los pacientes fueron ingresados! ????", vbInformation

End Sub
