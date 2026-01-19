# Principales/Terminal.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                         TERMINAL.PY - NOZHGESS v1.0
==============================================================================
Módulo de interfaz de terminal y logging del sistema.

Funcionalidades:
- Logging colorido a consola con emojis
- Logging a archivo para auditoría
- Resumen visual de pacientes con formato compacto

Autor: Sistema Nozhgess
==============================================================================
"""
from __future__ import annotations

# =============================================================================
#                              IMPORTS
# =============================================================================
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except Exception:
    # Fallback si colorama no está instalado
    class Dummy:
        RESET_ALL = ""
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = ""
        LIGHTBLACK_EX = LIGHTWHITE_EX = LIGHTYELLOW_EX = ""
        LIGHTGREEN_EX = LIGHTRED_EX = LIGHTBLUE_EX = LIGHTMAGENTA_EX = ""

    Fore = Dummy()
    Style = Dummy()

import logging
import os
from datetime import datetime
from typing import Dict, List, Any

# =============================================================================
#                         CONFIGURACIÓN DE LOGGING
# =============================================================================

# Crear carpeta logs si no existe
LOG_DIR = os.path.join(os.getcwd(), "logs")
if not os.path.exists(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
    except Exception:
        LOG_DIR = os.getcwd()

# Archivo de log con timestamp
LOG_FILE = os.path.join(LOG_DIR, f"nozhgess_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# =============================================================================
#                         MODO DEBUG (TOGGLE)
# =============================================================================
# El modo DEBUG se controla desde el archivo de misión (Mision_Actual.py)
# Si no se puede importar, default = False (producción)

try:
    from C_Mezclador.Mision_Actual import DEBUG as DEBUG_MODE
except ImportError:
    DEBUG_MODE = False  # Default: modo producción (logs limpios)

# =============================================================================
#                         CONFIGURACIÓN DE LOGGING
# =============================================================================

# Configurar logger
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
    encoding='utf-8',
    force=True
)


def _log_to_file(level: str, msg: str) -> None:
    """Escribe mensaje al archivo de log."""
    if level == "INFO":
        logging.info(msg)
    elif level == "WARN":
        logging.warning(msg)
    elif level == "ERROR":
        logging.error(msg)
    elif level == "OK":
        logging.info(f"[OK] {msg}")


def safe_print(msg: str) -> None:
    """Imprime mensaje manejando errores de encoding."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', 'replace').decode('ascii'))


# =============================================================================
#                       FUNCIONES DE LOGGING
# =============================================================================

def log_info(msg: str) -> None:
    """Log de información general."""
    # FILTRO: Solo muestra si DEBUG_MODE está activo
    if DEBUG_MODE:
        safe_print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {msg}")
    _log_to_file("INFO", msg)


def log_ok(msg: str) -> None:
    """Log de operación exitosa."""
    # FILTRO: Solo muestra si DEBUG_MODE está activo
    if DEBUG_MODE:
        safe_print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} {msg}")
    _log_to_file("OK", msg)


def log_warn(msg: str) -> None:
    """Log de advertencia."""
    # FILTRO: Solo muestra si DEBUG_MODE está activo
    if DEBUG_MODE:
        safe_print(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} {msg}")
    _log_to_file("WARN", msg)


def log_error(msg: str) -> None:
    """Log de error - SIEMPRE se muestra."""
    # Los errores SIEMPRE se muestran, independiente del DEBUG_MODE
    safe_print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")
    _log_to_file("ERROR", msg)


# =============================================================================
#                    PALETA DE COLORES PARA TERMINAL
# =============================================================================

C_BARRA = Fore.LIGHTBLACK_EX      # Separador |
C_INDICE = Fore.YELLOW            # [1/54]
C_HORA = Fore.LIGHTWHITE_EX       # Hora
C_NOMBRE = Fore.CYAN              # Nombre paciente
C_RUT = Fore.GREEN                # RUT
C_FECHA = Fore.MAGENTA            # Fecha
C_EXITO = Fore.GREEN              # Éxito
C_FALLO = Fore.RED                # Fallo
C_NARANJA = Fore.LIGHTYELLOW_EX   # Advertencia
C_ROJO = Fore.RED                 # Error
C_SI = Fore.LIGHTGREEN_EX         # Valor positivo
C_NO = Fore.LIGHTRED_EX           # Valor negativo
C_M1_LABEL = Fore.LIGHTBLUE_EX    # Misión 1
C_M2_LABEL = Fore.LIGHTMAGENTA_EX # Misión 2
RESET = Style.RESET_ALL


# =============================================================================
#                    RESUMEN VISUAL DE PACIENTE (COMPACTO)
# =============================================================================

def resumen_paciente(i: int, total: int, nombre: str, rut: str, fecha: str,
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

    # Línea 1: Información del paciente (CON espacios extra para seguridad visual)
    linea_info = (
        f"🔥 {C_INDICE}[{i}/{total}]{RESET} 🔥 {b} "
        f"⏳ {C_HORA}{now}{RESET} ⏳ {b} "
        f"🤹🏻  {C_NOMBRE}{nombre_str}{RESET}  🤹🏻 {b} "
        f"🪪  {C_RUT}{rut}{RESET} 🪪  {b} "
        f"🗓️  {C_FECHA}{fecha}{RESET}  🗓️"
    )

    # Línea 3: Datos de casos
    datos_segments = []
    resultado_segments = []

    for idx, res in enumerate(resultados):
        m_num = idx + 1
        color_lbl = C_M1_LABEL if m_num == 1 else C_M2_LABEL

        # Mini tabla
        mini_val = "Sí" if (res.get("Caso") or "Sin caso") != "Sin caso" else "No"
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
        mini_found = (res.get("Caso") or "Sin caso") != "Sin caso"
        obs_txt = res.get("Observación", "")
        obs_critica = any(x in obs_txt for x in ["Excluyente", "Edad", "Fallecido"])

        if not mini_found:
            st_msg, st_col = "⚠️ Sin Caso ⚠️", C_NARANJA  # Doble ⚠️
        elif obs_critica:
            st_msg, st_col = "⚠️ Observación ⚠️", C_NARANJA  # Doble ⚠️
        else:
            st_msg, st_col = "✅ OK ✅", C_EXITO

        resultado_segments.append(f"{color_lbl}M{m_num}:{RESET} {st_col}{st_msg}{RESET}")

    linea_datos = f" {b} ".join(datos_segments)

    # Línea 5: Resultado final
    if paciente_saltado:
        linea_resultado = f"{C_ROJO}♻️ Saltado ♻️({max_reintentos} reintentos){RESET}"
    elif not paciente_ok:
        linea_resultado = f"{C_FALLO}❌ Error Crítico ❌{RESET}"
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


def mostrar_banner(mision: str, archivo: str, total_filas: int) -> None:
    """
    Muestra un banner de inicio bonito con la configuración.
    
    SIEMPRE se muestra (independiente de DEBUG_MODE).
    
    Args:
        mision: Nombre de la misión
        archivo: Ruta del archivo de entrada
        total_filas: Número de filas a procesar
    """
    archivo_corto = os.path.basename(archivo) if archivo else "N/A"
    
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
║                           🔥 NOZHGESS v1.0 🔥                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  📋 Misión: {Fore.YELLOW}{mision[:60]:<60}{Fore.CYAN} ║
║  📂 Archivo: {Fore.GREEN}{archivo_corto[:59]:<59}{Fore.CYAN} ║
║  👥 Pacientes: {Fore.MAGENTA}{total_filas:<57}{Fore.CYAN} ║
╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    safe_print(banner)


# =============================================================================
#                      RESUMEN FINAL DE EJECUCIÓN
# =============================================================================

def mostrar_resumen_final(exitosos: int, fallidos: int, saltados: int, 
                          tiempo_inicio: datetime, archivo_salida: str) -> None:
    """
    Muestra resumen final de la ejecución.
    
    Args:
        exitosos: Pacientes procesados correctamente
        fallidos: Pacientes con errores
        saltados: Pacientes saltados
        tiempo_inicio: Datetime de inicio
        archivo_salida: Ruta del archivo generado
    """
    tiempo_total = datetime.now() - tiempo_inicio
    minutos = int(tiempo_total.total_seconds() // 60)
    segundos = int(tiempo_total.total_seconds() % 60)
    
    total = exitosos + fallidos + saltados
    pct_exito = (exitosos / total * 100) if total > 0 else 0
    
    archivo_corto = os.path.basename(archivo_salida) if archivo_salida else "N/A"
    
    resumen = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
║                           📊 RESUMEN FINAL 📊                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  ✅ Exitosos:    {Fore.GREEN}{exitosos:<61}{Fore.CYAN} ║
║  ❌ Fallidos:    {Fore.RED}{fallidos:<61}{Fore.CYAN} ║
║  ♻️  Saltados:    {Fore.YELLOW}{saltados:<61}{Fore.CYAN} ║
║  📈 Tasa éxito:  {Fore.MAGENTA}{pct_exito:.1f}%{' ' * 57}{Fore.CYAN} ║
║  ⏱️  Tiempo:      {Fore.WHITE}{minutos}m {segundos}s{' ' * 54}{Fore.CYAN} ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  💾 Guardado en: {Fore.GREEN}{archivo_corto[:60]:<60}{Fore.CYAN} ║
╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    safe_print(resumen)
