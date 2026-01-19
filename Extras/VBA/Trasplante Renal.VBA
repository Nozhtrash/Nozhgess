Option Explicit

' ===========================
'  NORMALIZAR TEXTO
' ===========================
Function Normaliza(ByVal txt As String) As String
    txt = UCase$(txt)
    txt = Replace(txt, "Á", "A")
    txt = Replace(txt, "É", "E")
    txt = Replace(txt, "Í", "I")
    txt = Replace(txt, "Ó", "O")
    txt = Replace(txt, "Ú", "U")
    Normaliza = Trim$(txt)
End Function

' ===========================
'  EXTRAER MEDICAMENTO BASE
' ===========================
Function NombreBaseMed(ByVal desc As String) As String
    Dim t As String
    t = Normaliza(desc)
    
    If InStr(t, "AZATIOPRINA") > 0 Then
        NombreBaseMed = "AZATIOPRINA"
    ElseIf InStr(t, "PREDNISONA") > 0 Then
        NombreBaseMed = "PREDNISONA"
    ElseIf InStr(t, "TACROLIMUS") > 0 Then
        NombreBaseMed = "TACROLIMUS"
    ElseIf InStr(t, "MICOFENOLATO") > 0 Then
        NombreBaseMed = "MICOFENOLATO"
    ElseIf InStr(t, "CICLOSPORINA") > 0 Then
        NombreBaseMed = "CICLOSPORINA"
    ElseIf InStr(t, "SIROLIMUS") > 0 Then
        NombreBaseMed = "SIROLIMUS"
    ElseIf InStr(t, "EVEROLIMUS") > 0 Then
        NombreBaseMed = "EVEROLIMUS"
    Else
        NombreBaseMed = ""
    End If
End Function

' ===========================
'   MACRO PRINCIPAL
' ===========================
Sub AsignarProtocolos_MejorEncaje()

    Const COL_RUT As Long = 1          ' Hoja "digitar": RUT
    Const COL_MED_DIG As Long = 9      ' Hoja "digitar": Medicamento
    
    Const COL_PROTO As Long = 1        ' Hoja "protocolos": Protocolo
    Const COL_MED_PRO As Long = 3      ' Hoja "protocolos": Fármacos requeridos
    Const COL_COSTO As Long = 4        ' Hoja "protocolos": Arancel 2025 ($)
    
    Dim wsDig As Worksheet, wsPro As Worksheet, wsOut As Worksheet
    Set wsDig = ThisWorkbook.Worksheets("digitar")
    Set wsPro = ThisWorkbook.Worksheets("protocolos")
    Set wsOut = ThisWorkbook.Worksheets("orden")
    
    Dim dictPac As Object              ' RUT -> dict(medsPaciente)
    Dim dictProtMeds As Object         ' Protocolo -> dict(medsProtocolo)
    Dim dictProtCosto As Object        ' Protocolo -> costo
    
    Set dictPac = CreateObject("Scripting.Dictionary")
    Set dictProtMeds = CreateObject("Scripting.Dictionary")
    Set dictProtCosto = CreateObject("Scripting.Dictionary")
    
    Dim ultFila As Long, i As Long
    
    ' ==================================================
    ' 1) LEER PACIENTES Y SUS MEDICAMENTOS
    ' ==================================================
    ultFila = wsDig.Cells(wsDig.Rows.Count, COL_RUT).End(xlUp).Row
    
    Dim rut As Variant
    Dim medDesc As String, medBase As String
    
    For i = 2 To ultFila
        rut = CStr(wsDig.Cells(i, COL_RUT).Value)
        medDesc = CStr(wsDig.Cells(i, COL_MED_DIG).Value)
        medBase = NombreBaseMed(medDesc)
        
        If medBase <> "" Then
            If Not dictPac.Exists(rut) Then
                Set dictPac(rut) = CreateObject("Scripting.Dictionary")
            End If
            dictPac(rut)(medBase) = 1
        End If
    Next i
    
    ' ==================================================
    ' 2) LEER PROTOCOLOS (MEDS + COSTOS)
    ' ==================================================
    ultFila = wsPro.Cells(wsPro.Rows.Count, COL_MED_PRO).End(xlUp).Row
    
    Dim currentProto As String
    Dim reqText As String, costText As String
    Dim partes() As String, p As Long
    
    currentProto = ""
    
    For i = 2 To ultFila
        
        ' Si aparece algo en la col de protocolo, empezamos / cambiamos bloque
        If wsPro.Cells(i, COL_PROTO).Value <> "" Then
            currentProto = Trim$(wsPro.Cells(i, COL_PROTO).Value)
            If Not dictProtMeds.Exists(currentProto) Then
                Set dictProtMeds(currentProto) = CreateObject("Scripting.Dictionary")
            End If
        End If
        
        ' Costo (puede estar solo en una fila por protocolo)
        costText = CStr(wsPro.Cells(i, COL_COSTO).Value)
        If costText <> "" And currentProto <> "" Then
            costText = Replace(Replace(Replace(costText, "$", ""), ".", ""), ",", ".")
            dictProtCosto(currentProto) = Val(costText)
        End If
        
        ' Fármacos requeridos
        reqText = CStr(wsPro.Cells(i, COL_MED_PRO).Value)
        If reqText <> "" And currentProto <> "" Then
            reqText = Replace(reqText, "•", "")
            reqText = Normaliza(reqText)
            
            partes = Split(reqText, " O ")
            For p = LBound(partes) To UBound(partes)
                medBase = NombreBaseMed(partes(p))
                If medBase <> "" Then
                    dictProtMeds(currentProto)(medBase) = 1
                End If
            Next p
        End If
    Next i
    
    ' ==================================================
    ' 3) EVALUAR Y ASIGNAR PROTOCOLOS
    ' ==================================================
    wsOut.Cells.Clear
    wsOut.Range("A1:G1").Value = Array("RUT", "Medicamentos", "Protocolo", "Extra", "Costo", "Requerimientos", "Explicación")
    
    Dim fila As Long: fila = 2
    Dim medsP As Object, medsProt As Object
    Dim bestProto As String
    Dim bestExtra As Long
    Dim bestCost As Double
    Dim extraCount As Long
    Dim proto As Variant, m As Variant, medProt As Variant
    Dim explicacion As String
    Dim medsPacienteStr As String
    
    For Each rut In dictPac.Keys
        
        Set medsP = dictPac(rut)
        bestProto = ""
        bestExtra = 10 ^ 9
        bestCost = -1
        
        ' recorrer TODOS los protocolos
        For Each proto In dictProtMeds.Keys
            
            Set medsProt = dictProtMeds(proto)
            
            ' 1) protocolo válido solo si contiene TODOS los medicamentos del paciente
            Dim compatible As Boolean
            compatible = True
            For Each m In medsP.Keys
                If Not medsProt.Exists(m) Then
                    compatible = False
                    Exit For
                End If
            Next m
            
            If compatible Then
                ' 2) contar cuántos fármacos extra tiene el protocolo
                extraCount = 0
                For Each medProt In medsProt.Keys
                    If Not medsP.Exists(medProt) Then
                        extraCount = extraCount + 1
                    End If
                Next medProt
                
                ' 3) elegir el de MENOS extras y, si empatan, el MÁS CARO
                If extraCount < bestExtra _
                   Or (extraCount = bestExtra And dictProtCosto(proto) > bestCost) Then
                       
                    bestExtra = extraCount
                    bestCost = dictProtCosto(proto)
                    bestProto = CStr(proto)
                End If
            End If
        
        Next proto
        
        medsPacienteStr = Join(dictPac(rut).Keys, ", ")
        
        wsOut.Cells(fila, 1).Value = rut
        wsOut.Cells(fila, 2).Value = medsPacienteStr
        wsOut.Cells(fila, 3).Value = bestProto
        
        If bestProto <> "" Then
            wsOut.Cells(fila, 4).Value = bestExtra
            wsOut.Cells(fila, 5).Value = bestCost
            wsOut.Cells(fila, 6).Value = Join(dictProtMeds(bestProto).Keys, ", ")
            
            explicacion = "Paciente tiene [" & medsPacienteStr & "]. " & _
                          "Protocolo " & bestProto & " es compatible porque el protocolo contiene todos esos medicamentos. " & _
                          "Este protocolo tiene " & bestExtra & " medicamento(s) extra respecto al paciente. " & _
                          "Entre los protocolos compatibles con la misma diferencia, se eligió el de MAYOR costo (" & bestCost & ")."
            
            wsOut.Cells(fila, 7).Value = explicacion
        Else
            wsOut.Cells(fila, 4).Value = -1
            wsOut.Cells(fila, 6).Value = "SIN PROTOCOLO COMPATIBLE"
            wsOut.Cells(fila, 7).Value = "Paciente con [" & medsPacienteStr & "]: ningún protocolo contiene simultáneamente todos estos fármacos."
        End If
        
        fila = fila + 1
    Next rut
    
    MsgBox "Protocolos asignados con explicación detallada ?", vbInformation

End Sub


