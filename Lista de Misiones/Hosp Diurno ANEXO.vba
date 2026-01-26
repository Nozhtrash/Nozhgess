Sub HospitalDiurnoAdultoyJuvenilCONANEXO()

    Dim wsGlobal As Worksheet, wsAnexo As Worksheet, wsCarga As Worksheet
    Dim lastRowGlobal As Long
    Dim i As Long
    Dim nombrePaciente As String, rutCompleto As String
    Dim rutSinDV As String, dv As String
    Dim fechaAtencion As Variant
    Dim filaCarga As Long
    Dim busqueda As Range

    ' Referencias a las hojas
    Set wsGlobal = ThisWorkbook.Sheets("Global")
    Set wsAnexo = ThisWorkbook.Sheets("Anexo")
    Set wsCarga = ThisWorkbook.Sheets("Carga")

    ' Limpiar hoja Carga (excepto encabezado)
    wsCarga.Cells.ClearContents

    ' Encabezados
    With wsCarga
        .Range("A1").Value = "FECHA"
        .Range("B1").Value = "RUT"
        .Range("C1").Value = "DV"
        .Range("D1").Value = "PRESTACIONES"
        .Range("E1").Value = "Tipo"
        .Range("F1").Value = "PS-FAM"
        .Range("G1").Value = "ESPECIALIDAD"
    End With

    filaCarga = 2 ' empezamos en la fila 2

    lastRowGlobal = wsGlobal.Cells(wsGlobal.Rows.Count, "B").End(xlUp).Row

    For i = 9 To lastRowGlobal
        ' Limpiar el nombre, eliminar espacios extra y hacer todo minúscula
        nombrePaciente = LCase(Trim(wsGlobal.Cells(i, "B").Value))

        ' Validar nombre y fecha no vacíos
        If nombrePaciente <> "" And IsDate(wsGlobal.Cells(i, "K").Value) Then
            
            ' Buscar nombre en Anexo utilizando búsqueda parcial y sin considerar mayúsculas/minúsculas
            Set busqueda = wsAnexo.Columns("G").Find(What:=nombrePaciente, LookIn:=xlValues, LookAt:=xlPart, MatchCase:=False)
            
            If Not busqueda Is Nothing Then
                rutCompleto = wsAnexo.Cells(busqueda.Row, "F").Value ' RUT con puntos y guión

                ' Dividir RUT
                Dim parts() As String
                parts = Split(rutCompleto, "-")
                rutSinDV = Replace(parts(0), ".", "")
                dv = parts(1)

                fechaAtencion = wsGlobal.Cells(i, "K").Value

                ' Agregar fila a Carga
                With wsCarga
                    .Cells(filaCarga, "A").NumberFormat = "@"
                    .Cells(filaCarga, "A").Value = Format(fechaAtencion, "dd-mm-yyyy")
                    .Cells(filaCarga, "B").Value = rutSinDV
                    .Cells(filaCarga, "C").Value = dv
                    .Cells(filaCarga, "D").NumberFormat = "@"
                    .Cells(filaCarga, "D").Value = "0203010"
                    .Cells(filaCarga, "E").Value = "PPV"
                    .Cells(filaCarga, "F").Value = "2301"
                    .Cells(filaCarga, "G").Value = "" ' Puedes añadir la especialidad aquí si quieres
                End With

                filaCarga = filaCarga + 1
            Else
                MsgBox "? No se encontró el paciente: " & nombrePaciente & " en la hoja Anexo.", vbExclamation
            End If
        End If
    Next i

    MsgBox "? Proceso completado. Registros generados: " & filaCarga - 2, vbInformation

End Sub