import os
script_dir = os.path.dirname(os.path.abspath(__file__))
legacy_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir))) # Z_Utilidades probably
# Assume standard structure if run from root or subdirectory
target_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))), "D_Principales", "Terminal.py")
# Falback if not found: try known location relative to current file
if not os.path.exists(target_path):
     # Try relative to project root assumed from 'Utilidades'
     target_path = os.path.join(script_dir, "..", "..", "..", "Utilidades", "Principales", "Terminal.py")

if not os.path.exists(target_path):
    print(f"Warning: Could not find Terminal.py at {target_path}")
    exit(1)

with open(target_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar la función resumen_paciente (línea 162) y reemplazarla completamente
new_function = '''def resumen_paciente(i: int, total: int, nombre: str, rut: str, fecha: str,
                     flags: Dict[str, bool], resultados: List[Dict[str, Any]],
                     revisar_ipd: bool = True, revisar_oa: bool = True,
                     max_reintentos: int = 4) -> None:
    """
    Muestra resumen visual compacto del paciente procesado.
    Formato limpio sin espacios extras, según especificaciones del usuario.
    """
    now = datetime.now().strftime("%H:%M")
    b = f"{C_BARRA}|{RESET}"
    
    paciente_ok = flags.get("ok", False)
    paciente_saltado = flags.get("saltado", False)
    nombre_str = (str(nombre) if nombre else "SIN NOMBRE").upper()

    # Línea 1: Información del paciente (SIN espacios extras)
    linea_info = (
        f"🔥 {C_INDICE}[{i}/{total}]{RESET} 🔥 {b} "
        f"⏳ {C_HORA}{now}{RESET} ⏳ {b} "
        f"🤹🏻 {C_NOMBRE}{nombre_str}{RESET} 🤹🏻 {b} "
        f"🪪 {C_RUT}{rut}{RESET} 🪪 {b} "
        f"🗓️ {C_FECHA}{fecha}{RESET} 🗓️"
    )

    # Línea 3: Datos de casos
    datos_segments = []
    resultado_segments = []

    for idx, res in enumerate(resultados):
        m_num = idx + 1
        color_lbl = C_M1_LABEL if m_num == 1 else C_M2_LABEL

        # Mini tabla
        mini_val = "Sí" if (res.get("Caso Encontrado") or "Sin caso") != "Sin caso" else "No"
        mini_col = C_SI if mini_val == "Sí" else C_NO
        datos_segments.append(f"📋 {color_lbl}M{m_num}:{RESET} {mini_col}{mini_val}{RESET}")

        # IPD
        if revisar_ipd:
            ipd_val = "Sí" if res.get("Estado IPD") and res.get("Estado IPD") != "Sin IPD" else "No"
            ipd_col = C_SI if ipd_val == "Sí" else C_NO
            datos_segments.append(f"🔶 {color_lbl}IPD:{RESET} {ipd_col}{ipd_val}{RESET}")

        # OA
        if revisar_oa:
            oa_val = "Sí" if res.get("Código OA") else "No"
            oa_col = C_SI if oa_val == "Sí" else C_NO
            datos_segments.append(f"🔷 {color_lbl}OA:{RESET} {oa_col}{oa_val}{RESET}")

        # Resultado de la misión
        mini_found = (res.get("Caso Encontrado") or "Sin caso") != "Sin caso"
        obs_txt = res.get("Observación", "")
        obs_critica = any(x in obs_txt for x in ["Excluyente", "Edad", "Fallecido"])

        if not mini_found:
            st_msg, st_col = "⚠️ Sin Caso ⚠️", C_NARANJA  # Doble ⚠️
        elif obs_critica:
            st_msg, st_col = "⚠️ Obs ⚠️", C_NARANJA  # Doble ⚠️
        else:
            st_msg, st_col = "✅ OK", C_EXITO

        resultado_segments.append(f"{color_lbl}M{m_num}:{RESET} {st_col}{st_msg}{RESET}")

    linea_datos = f" {b} ".join(datos_segments)

    # Línea 5: Resultado final
    if paciente_saltado:
        linea_resultado = f"{C_ROJO}♻️ Saltado ({max_reintentos} reintentos){RESET}"
    elif not paciente_ok:
        linea_resultado = f"{C_FALLO}❌ Error Crítico{RESET}"
    else:
        linea_resultado = f"📊 {' {b} '.join(resultado_segments)}"

    # IMPRIMIR TODO
    try:
        print(linea_info)
        print()
        print(linea_datos)
        print()
        print(linea_resultado)
        print(f"{C_BARRA}{'─' * 90}{RESET}")
    except Exception:
        # Fallback simple si falla el formateo
        print(f"[{i}/{total}] {nombre} - {rut} - {'OK' if paciente_ok else 'ERROR'}")
        print("─" * 90)

'''

# Reemplazar desde línea 162 hasta encontrar la siguiente función
start = 161  # línea 162 en 0-indexed
end = start
for i in range(start, min(start + 150, len(lines))):
    if i > start + 5 and lines[i].startswith('def ') and 'mostrar_banner' in lines[i]:
        end = i
        break

# Reconstru con la función nueva
new_lines = lines[:start] + [new_function + '\n'] + lines[end:]

with open(target_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Terminal.py limpiado con formato correcto")
