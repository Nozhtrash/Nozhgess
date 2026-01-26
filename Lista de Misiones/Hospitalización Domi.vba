Sub IngresarDatosHospitalizaciónDomiciliaria()

    Dim wsAdulto As Worksheet

    Dim wsInfantil As Worksheet

    Dim wsCargaMasivaAdulto As Worksheet

    Dim wsCargaMasivaInfantil As Worksheet

    Dim lastRowAdulto As Long

    Dim lastRowInfantil As Long

    Dim lastRowCargaMasivaAdulto As Long

    Dim lastRowCargaMasivaInfantil As Long

    Dim i As Long

    Dim j As Long

    Dim fechaInicio As Date

    Dim fechaFin As Date

    Dim rut As String

    Dim dv As String

    Dim prestacion As String

   

    ' Definir las hojas

    Set wsAdulto = ThisWorkbook.Sheets("Adulto")

    Set wsInfantil = ThisWorkbook.Sheets("Infantil")

    Set wsCargaMasivaAdulto = ThisWorkbook.Sheets("Carga Masiva Adulto")

    Set wsCargaMasivaInfantil = ThisWorkbook.Sheets("Carga Masiva Infantil")

   

    ' Inicializar las filas de las hojas de carga masiva

    lastRowCargaMasivaAdulto = wsCargaMasivaAdulto.Cells(wsCargaMasivaAdulto.Rows.Count, "A").End(xlUp).Row

    lastRowCargaMasivaInfantil = wsCargaMasivaInfantil.Cells(wsCargaMasivaInfantil.Rows.Count, "A").End(xlUp).Row

   

    ' Procesar la hoja "Adulto"

    lastRowAdulto = wsAdulto.Cells(wsAdulto.Rows.Count, "A").End(xlUp).Row

    For i = 2 To lastRowAdulto

        fechaInicio = wsAdulto.Cells(i, 1).Value

        fechaFin = wsAdulto.Cells(i, 2).Value

        rut = wsAdulto.Cells(i, 7).Value

        prestacion = wsAdulto.Cells(i, 3).Value

        For j = fechaInicio To fechaFin

            lastRowCargaMasivaAdulto = lastRowCargaMasivaAdulto + 1

            wsCargaMasivaAdulto.Cells(lastRowCargaMasivaAdulto, 1).Value = j

            wsCargaMasivaAdulto.Cells(lastRowCargaMasivaAdulto, 2).Value = Left(rut, Len(rut) - 2)

            wsCargaMasivaAdulto.Cells(lastRowCargaMasivaAdulto, 3).Value = Right(rut, 1)

            wsCargaMasivaAdulto.Cells(lastRowCargaMasivaAdulto, 4).Value = prestacion

        Next j

    Next i

   

    ' Procesar la hoja "Infantil"

    lastRowInfantil = wsInfantil.Cells(wsInfantil.Rows.Count, "A").End(xlUp).Row

    For i = 2 To lastRowInfantil

        fechaInicio = wsInfantil.Cells(i, 1).Value

        fechaFin = wsInfantil.Cells(i, 2).Value

        rut = wsInfantil.Cells(i, 7).Value

        prestacion = wsInfantil.Cells(i, 3).Value

        For j = fechaInicio To fechaFin

            lastRowCargaMasivaInfantil = lastRowCargaMasivaInfantil + 1

            wsCargaMasivaInfantil.Cells(lastRowCargaMasivaInfantil, 1).Value = j

            wsCargaMasivaInfantil.Cells(lastRowCargaMasivaInfantil, 2).Value = Left(rut, Len(rut) - 2)

            wsCargaMasivaInfantil.Cells(lastRowCargaMasivaInfantil, 3).Value = Right(rut, 1)

            wsCargaMasivaInfantil.Cells(lastRowCargaMasivaInfantil, 4).Value = prestacion

        Next j

    Next i

    MsgBox "Se han Ingresado los Datos con Éxito :D By:ElMati"

End Sub