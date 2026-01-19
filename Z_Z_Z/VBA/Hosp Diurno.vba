Sub HospitalDiurnoCargadorActualizado()

    Dim wsGlobal As Worksheet, wsCarga As Worksheet
    Dim lastRowGlobal As Long
    Dim i As Long, filaCarga As Long
    Dim rutCompleto As String, rutSinDV As String, dv As String
    Dim fechaAtencion As Variant, codigoPrestacion As String, especialidad As String
    Dim parts() As String

    ' Referencias a las hojas
    Set wsGlobal = ThisWorkbook.Sheets("Global")
    Set wsCarga = ThisWorkbook.Sheets("Carga Masiva")

    ' Limpiar contenido anterior (dejando encabezado)
    wsCarga.Range("A2:G10000").ClearContents

    ' Encontrar última fila con datos
    lastRowGlobal = wsGlobal.Cells(wsGlobal.Rows.Count, "B").End(xlUp).Row
    filaCarga = 2

    For i = 2 To lastRowGlobal
        rutCompleto = Trim(wsGlobal.Cells(i, "E").Value) ' Run del Paciente
        fechaAtencion = wsGlobal.Cells(i, "L").Value     ' Fecha
        codigoPrestacion = Trim(wsGlobal.Cells(i, "J").Value)
        especialidad = Trim(wsGlobal.Cells(i, "M").Value)

        ' Validar campos necesarios
        If rutCompleto <> "" And IsDate(fechaAtencion) And codigoPrestacion <> "" Then
            ' Dividir RUT
            parts = Split(rutCompleto, "-")
            If UBound(parts) = 1 Then
                rutSinDV = Replace(parts(0), ".", "")
                dv = parts(1)

                ' Agregar a hoja de carga
                With wsCarga
                    .Cells(filaCarga, "A").NumberFormat = "@"
                    .Cells(filaCarga, "A").Value = Format(fechaAtencion, "dd-mm-yyyy")
                    .Cells(filaCarga, "B").Value = rutSinDV
                    .Cells(filaCarga, "C").Value = dv
                    .Cells(filaCarga, "D").Value = codigoPrestacion
                    .Cells(filaCarga, "E").Value = "PPV"
                    .Cells(filaCarga, "F").Value = "2301"
                    .Cells(filaCarga, "G").Value = especialidad
                End With

                filaCarga = filaCarga + 1
            End If
        End If
    Next i

    MsgBox "✅ Proceso finalizado. Se cargaron " & filaCarga - 2 & " registros.", vbInformation

End Sub