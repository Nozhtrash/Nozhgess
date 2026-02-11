Sub TransferirFAPDesdeMatíasACargaMasivaA()
    Dim wsMatias As Worksheet, wsCargaMasiva As Worksheet
    Dim ultimaFilaMatias As Long, ultimaFilaCarga As Long
    Dim i As Long
    Dim PS_FAM As String
    Dim listaPrestaciones As Object
    
    MsgBox "Transferencia en proceso, espere... By:Nozhtrash"
    
    ' Asignar hojas
    Set wsMatias = ThisWorkbook.Sheets("Matías")
    Set wsCargaMasiva = ThisWorkbook.Sheets("Carga Masiva")
    
    ' Crear lista de prestaciones con sus PS-FAM
    Set listaPrestaciones = CreateObject("Scripting.Dictionary")
    listaPrestaciones.Add "1103066", "2053"
    listaPrestaciones.Add "1202045N", "2144"
    listaPrestaciones.Add "1202060N", "2142"
    listaPrestaciones.Add "1302028", "2133"
    listaPrestaciones.Add "1302029", "2133"
    listaPrestaciones.Add "1701142", "2245"
    listaPrestaciones.Add "1701143", "2348"
    listaPrestaciones.Add "1701019", "2243"
    listaPrestaciones.Add "1701046N", "2250"
    listaPrestaciones.Add "1701050N", "2251"
    listaPrestaciones.Add "1701051N", "2251"
    listaPrestaciones.Add "1701052", "2252"
    listaPrestaciones.Add "1701131N", "2244"
    listaPrestaciones.Add "1701141N", "2245"
    listaPrestaciones.Add "1701142N", "2245"
    listaPrestaciones.Add "1703010", "2271"
    listaPrestaciones.Add "1703012", "2271"
    listaPrestaciones.Add "1703014N", "2274"
    listaPrestaciones.Add "1703017", "2271"
    listaPrestaciones.Add "1703025", "2262"
    listaPrestaciones.Add "1703056", "2347"
    listaPrestaciones.Add "1703107", "1740"
    listaPrestaciones.Add "1703117", "2272"
    listaPrestaciones.Add "1703163N", "2247"
    listaPrestaciones.Add "1703164", "2259"
    listaPrestaciones.Add "1703254", "2254"
    listaPrestaciones.Add "1703255", "2256"
    listaPrestaciones.Add "1703256", "2258"
    listaPrestaciones.Add "1703461", "2238"
    listaPrestaciones.Add "1703464", "2239"
    listaPrestaciones.Add "1704043", "2348"
    listaPrestaciones.Add "1704059", "2219"
    listaPrestaciones.Add "1801018", "2214"
    listaPrestaciones.Add "1801025", "2215"
    listaPrestaciones.Add "1801027", "2223"
    listaPrestaciones.Add "1801028", "2217"
    listaPrestaciones.Add "1801031", "2216"
    listaPrestaciones.Add "1801033", "2218"
    listaPrestaciones.Add "1801036", "2222"
    listaPrestaciones.Add "1801045", "2224"
    listaPrestaciones.Add "1802001", "2231"
    listaPrestaciones.Add "1802002", "2232"
    listaPrestaciones.Add "1802003", "2231"
    listaPrestaciones.Add "1802028N", "2234"
    listaPrestaciones.Add "1802029N", "2234"
    listaPrestaciones.Add "1802039N", "2346"
    listaPrestaciones.Add "1802047", "2225"
    listaPrestaciones.Add "1802060N", "2229"
    listaPrestaciones.Add "1802067N", "2229"
    listaPrestaciones.Add "1802068N", "2229"
    listaPrestaciones.Add "1802073N", "2231"
    listaPrestaciones.Add "1802074", "2231"
    listaPrestaciones.Add "1802081N", "2233"
    listaPrestaciones.Add "1802101", "2231"
    listaPrestaciones.Add "1802101N", "2231"
    listaPrestaciones.Add "1803001", "2228"
    listaPrestaciones.Add "1902060", "2040"
    listaPrestaciones.Add "1902061", "2040"
    listaPrestaciones.Add "1902066", "2040"
    listaPrestaciones.Add "1902082", "2041"
    listaPrestaciones.Add "1902090", "2042"
    listaPrestaciones.Add "2003004", "2201"
    listaPrestaciones.Add "2003005", "2201"
    listaPrestaciones.Add "2003010N", "2200"
    listaPrestaciones.Add "2003014N", "2200"
    listaPrestaciones.Add "2003015N", "2200"
    listaPrestaciones.Add "2003022", "2038"
    listaPrestaciones.Add "2003023", "2202"
    listaPrestaciones.Add "2003024", "2202"
    listaPrestaciones.Add "2104011", "2054"
    listaPrestaciones.Add "2104025N", "2137"
    listaPrestaciones.Add "2104042", "2059"
    listaPrestaciones.Add "2104048", "2061"
    listaPrestaciones.Add "2104051", "2060"
    listaPrestaciones.Add "2104053", "2052"
    listaPrestaciones.Add "2104055", "2058"
    listaPrestaciones.Add "2104073", "2057"
    listaPrestaciones.Add "2104144", "2055"
    listaPrestaciones.Add "2104153", "2052"
    listaPrestaciones.Add "2104159", "2062"
    listaPrestaciones.Add "2104162", "2063"
    listaPrestaciones.Add "2104167", "2056"
    listaPrestaciones.Add "2104174", "2072"
    listaPrestaciones.Add "2104190", "2078"
    listaPrestaciones.Add "2104228", "2048"
    listaPrestaciones.Add "2104229N", "2049"
    listaPrestaciones.Add "2104229NN", "2050"
    listaPrestaciones.Add "2104231", "2051"
    listaPrestaciones.Add "2104279", "2080"
    listaPrestaciones.Add "2104302", "2075"
    listaPrestaciones.Add "2104303", "2076"
    listaPrestaciones.Add "2104304", "2077"
    listaPrestaciones.Add "2104329", "2190"
    listaPrestaciones.Add "2104360", "2065"
    listaPrestaciones.Add "2104361", "2066"
    listaPrestaciones.Add "2104362", "2067"
    listaPrestaciones.Add "2104363", "2068"
    listaPrestaciones.Add "2104364", "2069"
    listaPrestaciones.Add "2106001", "2079"
    listaPrestaciones.Add "2106002", "2079"
    listaPrestaciones.Add "2106003", "2079"
    listaPrestaciones.Add "2501010", "2197"
    listaPrestaciones.Add "2501012", "2194"
    listaPrestaciones.Add "2505645", "2363"
    listaPrestaciones.Add "2505912", "2082"
    listaPrestaciones.Add "2505913", "2083"
    listaPrestaciones.Add "2505976", "2027"
    listaPrestaciones.Add "2505977", "2028"
    listaPrestaciones.Add "6002009", "2175"
    listaPrestaciones.Add "6002013", "2177"
    listaPrestaciones.Add "6003006", "2127"
    listaPrestaciones.Add "8002022", "2196"
    listaPrestaciones.Add "8002023", "2195"
    listaPrestaciones.Add "8002025", "2043"
    listaPrestaciones.Add "8002029", "2047"
    listaPrestaciones.Add "8002032", "2139"
    
    ' Última fila de "Matías"
    ultimaFilaMatias = wsMatias.Cells(wsMatias.Rows.Count, "K").End(xlUp).Row
    
    ' Empezar desde la primera fila vacía en "Carga Masiva"
    ultimaFilaCarga = wsCargaMasiva.Cells(wsCargaMasiva.Rows.Count, "A").End(xlUp).Row + 1
    
    ' Loop a través de las filas de "Matías"
    For i = 2 To ultimaFilaMatias ' Asumiendo que la primera fila es el encabezado
        Dim prestacion As String
        prestacion = wsMatias.Cells(i, "K").Value
        
        ' Verificar si la prestación está en la lista
        If listaPrestaciones.Exists(prestacion) Then
            ' Copiar los datos a "Carga Masiva"
            wsCargaMasiva.Cells(ultimaFilaCarga, "A").Value = wsMatias.Cells(i, "A").Value ' Fecha
            wsCargaMasiva.Cells(ultimaFilaCarga, "B").Value = wsMatias.Cells(i, "C").Value ' Rut del Paciente
            wsCargaMasiva.Cells(ultimaFilaCarga, "D").Value = wsMatias.Cells(i, "K").Value ' Prestación
            wsCargaMasiva.Cells(ultimaFilaCarga, "F").Value = listaPrestaciones(prestacion) ' PS-FAM
            
            ' Aplicar formato a la fila transferida en "Matías"
            With wsMatias.Rows(i)
                .Interior.Color = RGB(255, 0, 0) ' Fondo rojo
                .Font.Color = RGB(255, 255, 255) ' Texto blanco
                .Font.Bold = True ' Texto en negrita
            End With
            
            ' Incrementar la fila de carga masiva
            ultimaFilaCarga = ultimaFilaCarga + 1
        End If
    Next i
    
    MsgBox "Transferencia Completada By:Nozhtrash", vbInformation
End Sub
