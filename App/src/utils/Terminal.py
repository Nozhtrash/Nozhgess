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
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# =============================================================================
#                         CONFIGURACIÓN DE LOGGING
# =============================================================================

# Crear carpeta logs si no existe
# Usamos ruta relativa para encontrar la raíz del proyecto
ruta_utils = os.path.dirname(os.path.abspath(__file__))
ruta_src = os.path.dirname(ruta_utils)
ruta_app = os.path.dirname(ruta_src)
BASE_DIR = os.path.dirname(ruta_app) # True Root
LOG_DIR = os.path.join(BASE_DIR, "Logs")

if not os.path.exists(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
    except Exception:
        # Si falla, usar directorio temporal o local como fallback
        LOG_DIR = os.path.join(BASE_DIR, "logs_fallback")
        os.makedirs(LOG_DIR, exist_ok=True)

# Función de Rotación de Logs: Mantener solo los N logs más recientes
def rotar_logs(directorio: str, mantener: int = 4) -> None:
    """
    Elimina los logs más antiguos, manteniendo solo los 'mantener' más recientes.
    Evita que la carpeta de logs se llene de basura.
    """
    try:
        # Listar archivos .log en el directorio
        archivos = [
            os.path.join(directorio, f) 
            for f in os.listdir(directorio) 
            if f.endswith('.log')
        ]
        
        # Si hay más archivos de los permitidos
        if len(archivos) > mantener:
            # Ordenar por fecha de modificación (el más viejo primero)
            archivos.sort(key=os.path.getmtime)
            
            # Calcular cuántos borrar
            borrar_count = len(archivos) - mantener
            
            # Borrar los más viejos
            for i in range(borrar_count):
                os.remove(archivos[i])
                print(f"🗑️ Log antiguo eliminado: {os.path.basename(archivos[i])}")
                
    except Exception as e:
        print(f"⚠️ Error rotando logs: {e}")

# Ejecutar rotación antes de crear el nuevo
rotar_logs(LOG_DIR, mantener=4)

# Archivo de log con timestamp
LOG_FILE = os.path.join(LOG_DIR, f"nozhgess_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# =============================================================================
#                         MODO DEBUG (TOGGLE)
# =============================================================================
# El modo DEBUG permite una inspección profunda ("Deep Debug")
# Captura trazas completas y variables de estado para aprendizaje futuro.

try:
    # Intentar importar desde la raíz del proyecto
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)
    import Mision_Actual.Mision_Actual as ma
    DEBUG_MODE = ma.DEBUG_MODE if hasattr(ma, "DEBUG_MODE") else False
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
#                    FUNCIONES DE LOGGING AVANZADAS
# =============================================================================

def get_system_stats() -> str:
    """Retorna string con uso de CPU y RAM (si psutil está disponible)."""
    if not PSUTIL_AVAILABLE:
        return ""
    try:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        return f" [CPU: {cpu}% | RAM: {mem}%]"
    except:
        return ""

def log_debug(msg: str) -> None:
    """
    Log de debug DETALLADO - Solo en DEBUG_MODE.
    Incluye milisegundos y stats del sistema.
    """
    # Timestamp de alta precisión para debug
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    stats = get_system_stats()
    
    full_msg = f"[{timestamp}]{stats} {msg}"
    
    # Escribir siempre al log (DEBUG se filtra en el handler si es necesario, pero aquí forzamos INFO para que se guarde)
    # Usamos prefijo [DEBUG] para que el parser de runner.py lo detecte
    _log_to_file("INFO", f"[DEBUG] {full_msg}")


def log_step(paso: str, rut: str = None, extra: str = None) -> None:
    """
    Log de paso importante con contexto.
    
    Args:
        paso: Nombre del paso (ej: "Buscando paciente", "Leyendo IPD")
        rut: RUT del paciente actual (opcional)
        extra: Información adicional (opcional)
    """
    ctx_parts = []
    if rut:
        ctx_parts.append(f"RUT={rut}")
    if extra:
        ctx_parts.append(extra)
    
    ctx = f" | {' | '.join(ctx_parts)}" if ctx_parts else ""
    
    # En debug mode, añadir stats al paso
    if DEBUG_MODE:
        stats = get_system_stats()
        msg = f"📌 {paso}{ctx}{stats}"
    else:
        msg = f"📌 {paso}{ctx}"
    log_info(msg)


def log_separator(titulo: str = None) -> None:
    """Imprime separador visual con título opcional."""
    if titulo:
        sep = f"━━━━━ {titulo} ━━━━━"
    else:
        sep = "━" * 50
    
    if DEBUG_MODE:
        safe_print(f"{Fore.LIGHTBLACK_EX}{sep}{Style.RESET_ALL}")
    _log_to_file("INFO", sep)


# =============================================================================
#                    CONTEXT MANAGER DE TIMING
# =============================================================================

import time
from contextlib import contextmanager

@contextmanager
def timing_block(nombre: str, show_start: bool = True):
    """
    Context manager para medir y mostrar tiempo de ejecución.
    
    Uso:
        with timing_block("Leer IPD"):
            # código que se mide...
        # Automáticamente imprime: "└─ Leer IPD → 123ms"
    
    Args:
        nombre: Nombre de la operación para mostrar
        show_start: Si mostrar mensaje de inicio (default: True)
    """
    from src.utils.DEBUG import should_show_timing
    
    t0 = time.time()
    
    if show_start and should_show_timing():
        safe_print(f"{Fore.LIGHTBLACK_EX}  └─ {nombre}...{Style.RESET_ALL}")
    
    try:
        yield
    finally:
        dt = (time.time() - t0) * 1000
        if should_show_timing():
            safe_print(f"{Fore.LIGHTBLACK_EX}  └─ {nombre} → {dt:.0f}ms{Style.RESET_ALL}")
        # Siempre loguear a archivo
        _log_to_file("INFO", f"⏱️ {nombre}: {dt:.0f}ms")


def timing_msg(nombre: str, dt_ms: float) -> None:
    """
    Imprime mensaje de timing directamente.
    
    Args:
        nombre: Nombre de la operación
        dt_ms: Tiempo en milisegundos
    """
    from src.utils.DEBUG import should_show_timing
    
    if should_show_timing():
        safe_print(f"{Fore.LIGHTBLACK_EX}  └─ {nombre} → {dt_ms:.0f}ms{Style.RESET_ALL}")
    _log_to_file("INFO", f"⏱️ {nombre}: {dt_ms:.0f}ms")


# =============================================================================
#                    PALETA DE COLORES PARA TERMINAL
# =============================================================================

# 🎨 PALETA DE COLORES BRILLANTES (mejor visibilidad en terminal oscura)
C_BARRA = Fore.WHITE              # Separador | (blanco brillante)
C_INDICE = Fore.YELLOW            # [1/54] (oro - ya es brillante)
C_HORA = Fore.LIGHTCYAN_EX        # Hora (celeste brillante)
C_NOMBRE = Fore.LIGHTCYAN_EX      # Nombre paciente (celeste)
C_RUT = Fore.LIGHTGREEN_EX        # RUT (verde brillante)
C_FECHA = Fore.LIGHTMAGENTA_EX    # Fecha (rosado/magenta brillante)
C_EXITO = Fore.LIGHTGREEN_EX      # Éxito (verde neón)
C_FALLO = Fore.LIGHTRED_EX        # Fallo (rojo neón)
C_NARANJA = Fore.LIGHTYELLOW_EX   # Advertencia (amarillo brillante)
C_ROJO = Fore.LIGHTRED_EX         # Error (rojo neón)
C_SI = Fore.LIGHTGREEN_EX         # Valor positivo (verde neón)
C_NO = Fore.LIGHTRED_EX           # Valor negativo (rojo neón)
C_M1_LABEL = Fore.LIGHTCYAN_EX    # Misión 1 (celeste)
C_M2_LABEL = Fore.LIGHTMAGENTA_EX # Misión 2 (rosado)
RESET = Style.RESET_ALL


# =============================================================================
#                    RESUMEN VISUAL DE PACIENTE (COMPACTO)
# =============================================================================

def resumen_paciente(i: int, total: int, nombre: str, rut: str, fecha: str,
                     flags: Dict[str, bool], resultados: List[Dict[str, Any]],
                     revisar_ipd: bool = True, revisar_oa: bool = True,
                     revisar_aps: bool = False, revisar_sic: bool = False,
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
        f"🔥 {C_INDICE}[{i}/{total}]{RESET}🔥 {b} "
        f"⏳ {C_HORA}{now}{RESET} ⏳ {b} "
        f"🤹🏻 {C_NOMBRE}{nombre_str}{RESET} 🤹🏻 {b} "
        f"🪪  {C_RUT}{rut}{RESET} 🪪  {b} "
        f"🗓️  {C_FECHA}{fecha}{RESET} 🗓️"
    )

    # Línea 3: Datos de casos - AHORA UNA LÍNEA POR MISIÓN
    lineas_misiones = []

    for idx, res in enumerate(resultados):
        m_num = idx + 1
        color_lbl = C_M1_LABEL if m_num == 1 else C_M2_LABEL

        # Mini tabla
        mini_val = "Sí" if (res.get("Caso") or "Sin caso") != "Sin caso" else "No"
        mini_col = C_SI if mini_val == "Sí" else C_NO
        
        # IPD
        ipd_str = ""
        if revisar_ipd:
            ipd_val = "Sí" if res.get("Estado IPD") and res.get("Estado IPD") != "Sin IPD" else "No"
            ipd_col = C_SI if ipd_val == "Sí" else C_NO
            ipd_str = f" {b} 🔶 {color_lbl}IPD:{RESET} {ipd_col}{ipd_val}{RESET}"

        # OA
        oa_str = ""
        if revisar_oa:
            oa_val = "Sí" if res.get("Código OA") else "No"
            oa_col = C_SI if oa_val == "Sí" else C_NO
            oa_str = f" {b} 🔷 {color_lbl}OA:{RESET} {oa_col}{oa_val}{RESET}"

        # APS (🏥 = hospital/clinic)
        aps_str = ""
        if revisar_aps:
            aps_val = "Sí" if res.get("Fecha APS") and res.get("Fecha APS") != "" else "No"
            aps_col = C_SI if aps_val == "Sí" else C_NO
            aps_str = f" {b} 🏥 {color_lbl}APS:{RESET} {aps_col}{aps_val}{RESET}"

        # SIC (📨 = interconsulta/referral)
        sic_str = ""
        if revisar_sic:
            sic_val = "Sí" if res.get("Fecha SIC") and res.get("Fecha SIC") != "" else "No"
            sic_col = C_SI if sic_val == "Sí" else C_NO
            sic_str = f" {b} 📨 {color_lbl}SIC:{RESET} {sic_col}{sic_val}{RESET}"

        # Resultado de la misión
        mini_found = (res.get("Caso") or "Sin caso") != "Sin caso"
        obs_txt = res.get("Observación", "")
        obs_critica = any(x in obs_txt for x in ["Excluyente", "Edad", "Fallecido"])

        if not mini_found:
            st_msg, st_col = "⚠️  Sin Caso  ⚠️", C_NARANJA  # Espacios extra
        elif obs_critica:
            st_msg, st_col = "⚠️  Observación  ⚠️", C_NARANJA  # Espacios extra
        else:
            st_msg, st_col = "✅ OK ✅", C_EXITO

        # Construir línea completa de la misión
        linea_mision = (
            f"📋 {color_lbl}M{m_num}:{RESET} {mini_col}{mini_val}{RESET}"
            f"{ipd_str}{oa_str}{aps_str}{sic_str}"
            f" {b} 📊 {color_lbl}M{m_num}:{RESET} {st_col}{st_msg}{RESET}"
        )
        lineas_misiones.append(linea_mision)

    # Línea de resultado especial para casos de error
    if paciente_saltado:
        linea_resultado_especial = f"{C_ROJO}♻️ Saltado ♻️({max_reintentos} reintentos){RESET}"
    elif not paciente_ok:
        linea_resultado_especial = f"{C_FALLO}❌ Error Crítico ❌{RESET}"
    else:
        linea_resultado_especial = None

    # IMPRIMIR TODO
    # IMPRIMIR TODO
    try:
        print(linea_info)
        print()
        
        # Imprimir cada misión en su propia línea con separación
        for i_m, linea_m in enumerate(lineas_misiones):
            print(linea_m)
            # Siempre espacio después de misión
            print() 
        
        # Si hay error especial, mostrarlo
        if linea_resultado_especial:
            print(linea_resultado_especial)
            print() # Espacio
        
        # Separación extra para el siguiente paciente (Total 2-3 espacios visuales)
        print() 
        print() # Espacio extra solicitado 
        
    except Exception:
        # Fallback simple si falla el formateo
        print(f"[{i}/{total}] {nombre} - {rut} - {'OK' if paciente_ok else 'ERROR'}")
        print()


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
