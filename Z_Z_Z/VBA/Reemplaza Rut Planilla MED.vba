Sub ReemplazarRUTsMalosConBuenosPlanillaMedicamentos()
    Dim ws As Worksheet
    Set ws = ActiveSheet

    Dim filaMalosInicio As Long: filaMalosInicio = 2
    Dim filaMalosFin As Long: filaMalosFin = 500 ' Puedes ajustarlo si tienes más filas arriba

    Dim filaBuenosInicio As Long: filaBuenosInicio = 501 ' Puedes ajustar esto si tus "amarillos" empiezan en otra fila
    Dim filaBuenosFin As Long
    filaBuenosFin = ws.Cells(ws.Rows.Count, "B").End(xlUp).Row

    Dim i As Long, j As Long

    For i = filaBuenosInicio To filaBuenosFin
        ' Solo procesamos si la celda del RUT (columna E) es amarilla
        If ws.Cells(i, 5).Interior.Color = RGB(255, 255, 0) Then

            Dim apePatBueno As String: apePatBueno = Trim(UCase(ws.Cells(i, 2).Value))
            Dim apeMatBueno As String: apeMatBueno = Trim(UCase(ws.Cells(i, 3).Value))
            Dim nomBueno As String: nomBueno = Trim(UCase(ws.Cells(i, 4).Value))
            Dim rutBueno As String: rutBueno = Trim(ws.Cells(i, 5).Value)

            ' Buscar coincidencia en pacientes de arriba
            For j = filaMalosInicio To filaMalosFin
                Dim apePatMalo As String: apePatMalo = Trim(UCase(ws.Cells(j, 2).Value))
                Dim apeMatMalo As String: apeMatMalo = Trim(UCase(ws.Cells(j, 3).Value))
                Dim nomMalo As String: nomMalo = Trim(UCase(ws.Cells(j, 4).Value))
                Dim rutMalo As String: rutMalo = Trim(ws.Cells(j, 5).Value)

                If apePatBueno = apePatMalo And apeMatBueno = apeMatMalo And nomBueno = nomMalo Then
                    If rutMalo <> rutBueno Then
                        ' Corregir RUT y marcar con estilo
                        ws.Cells(j, 5).Value = rutBueno
                        With ws.Cells(j, 5)
                            .Interior.Color = RGB(0, 32, 96) ' Azul oscuro
                            .Font.Color = RGB(255, 255, 255) ' Blanco
                            .Font.Bold = True
                        End With
                    End If
                    Exit For
                End If
            Next j
        End If
    Next i

    MsgBox "RUTs corregidos con éxito solo si estaban mal. ¡Listo el pollo! 🐔💙", vbInformation
End Sub