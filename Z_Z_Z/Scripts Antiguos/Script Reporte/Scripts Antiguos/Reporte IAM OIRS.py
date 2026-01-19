import os
import time
import pandas as pd
from datetime import datetime, date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from colorama import Fore, Style, init

# =========================
# CONFIG
# =========================
EDGE_DRIVER_PATH = r"C:\Windows\System32\msedgedriver.exe"
DEBUG_PORT = "localhost:9222"  # Usar Edge ya abierto con este puerto
URL_FRICKE = "https://fricke.experthis.cl/sgh/interface.php"

# Excel de entrada (Reporte) y hoja IAM
RUTA_EXCEL_REPORTE = r"C:\Users\Usuario HGF\Desktop\Trabajo\Reporte Farmacia 25-31 Agosto.xlsx"
HOJA_IAM = "IAM Fricke"

# Mapeo de columnas (0-based): B = 1, D = 3 (opcional), F = 5
COL_RUT = 1
COL_NOMBRE = 3   # pon None si tu hoja no tiene nombre
COL_FECHA = 5

# Carpeta de salida
RUTA_CARPETA_SALIDA = r"C:\Users\Usuario HGF\Desktop\Trabajo\Extra\Revisiones"

# XPaths/Selectores FRICKE
XPATH_INPUT_RUT = "/html/body/div[2]/center/div/div[2]/form/table/tbody/tr[10]/td[2]/input"
XPATH_BTN_LISTAR = "/html/body/div[2]/center/div/div[2]/form/table/tbody/tr[11]/td/center/input[1]"
XPATH_TBODY = "/html/body/div[2]/center/div/div[3]/table/tbody"

# Spinners conocidos
CSS_SPINNER_IMG = "#carga > div > img"
XPATH_SPINNER_DIV = "/html/body/div[3]/div"

# =========================
# UTILS
# =========================
init(autoreset=True)
EMOJI_TARGET, EMOJI_OK, EMOJI_NO = "🎯", "✅", "❌"

def log_header(nombre, rut, fexcel_str):
    print(
        f"{EMOJI_TARGET} {Fore.BLUE}{nombre or '(sin nombre)'}{Style.RESET_ALL} "
        f"({Fore.MAGENTA}{rut}{Style.RESET_ALL}) | "
        f"Fecha objetivo: {Fore.GREEN}{fexcel_str}{Style.RESET_ALL}"
    )

def log_result(hosp, desde_str, hasta_str):
    if hosp:
        print(
            f"{Fore.GREEN}{EMOJI_OK} Hospitalizado: Sí{Style.RESET_ALL} "
            f"| Desde: {Fore.CYAN}{desde_str}{Style.RESET_ALL} "
            f"| Hasta: {Fore.CYAN}{hasta_str}{Style.RESET_ALL}\n"
        )
    else:
        print(f"{Fore.RED}{EMOJI_NO} Hospitalizado: No{Style.RESET_ALL}\n")

def parse_fecha_dmy(value):
    """Devuelve date o None. Soporta dd/mm/yyyy, dd/mm/yyyy HH:MM y yyyy-mm-dd."""
    s = str(value).strip()
    for fmt in ("%d/%m/%Y", "%d/%m/%Y %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s.split()[0], fmt).date()
        except Exception:
            pass
    return None

def fmt_dmy(d: date | None) -> str:
    return d.strftime("%d/%m/%Y") if isinstance(d, date) else "—"

def ir_a_fricke(driver):
    """Asegura estar en interface.php y que el input RUT esté presente."""
    if URL_FRICKE not in driver.current_url:
        driver.get(URL_FRICKE)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, XPATH_INPUT_RUT))
    )

def esperar_spinner_fricke(driver):
    """Intenta esperar a que desaparezca algún spinner; si no, fallback a sleep corto."""
    # Si alguno de los dos desaparece, seguimos
    for locator in [(By.CSS_SELECTOR, CSS_SPINNER_IMG), (By.XPATH, XPATH_SPINNER_DIV)]:
        try:
            WebDriverWait(driver, 6).until(EC.invisibility_of_element_located(locator))
            return
        except TimeoutException:
            pass
    time.sleep(3)  # fallback conservador

def elegir_mejor_rango(matching_ranges, fecha_obj):
    """
    De múltiples rangos que contienen la fecha, elige el más cercano a la fecha:
    el de Ingreso más reciente <= fecha_obj.
    matching_ranges: lista de tuplas (ingreso: date, egreso: date|None)
    """
    # Ordenamos por ingreso desc, y tomamos el primero
    matching_ranges.sort(key=lambda x: x[0], reverse=True)
    return matching_ranges[0] if matching_ranges else (None, None)

def buscar_rango_hosp(driver, rut, fecha_obj):
    """
    Retorna (hospitalizado_bool, desde_date|None, hasta_date|None).
    Busca en FRICKE si fecha_obj ∈ [ingreso, egreso] en alguna fila
    (o ingreso ≤ fecha_obj si egreso vacío).
    Si hay múltiples, elige el rango con ingreso más cercano (más reciente <= fecha_obj).
    """
    ir_a_fricke(driver)

    # Ingresar RUT
    inp = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, XPATH_INPUT_RUT)))
    inp.clear()
    inp.send_keys(rut)

    # Listar
    btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATH_BTN_LISTAR)))
    driver.execute_script("arguments[0].click();", btn)

    # Esperar carga
    esperar_spinner_fricke(driver)

    # Leer la tabla
    try:
        tbody = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, XPATH_TBODY)))
    except TimeoutException:
        # Puede no haber resultados
        return False, None, None

    filas = tbody.find_elements(By.TAG_NAME, "tr")
    matching = []

    # tr[1] suele ser header; revisamos desde tr[2] => índice 1
    for i in range(1, len(filas)):
        tds = filas[i].find_elements(By.TAG_NAME, "td")
        # Necesitamos al menos 7 columnas; ingreso = td[6], egreso = td[7]
        if len(tds) < 7:
            continue

        f_ing = parse_fecha_dmy(tds[5].text)  # td[6] → index 5
        f_egr = parse_fecha_dmy(tds[6].text)  # td[7] → index 6

        if not f_ing:
            continue

        if f_egr:
            # Rango cerrado
            if f_ing <= fecha_obj <= f_egr:
                matching.append((f_ing, f_egr))
        else:
            # Rango abierto (sin egreso)
            if fecha_obj >= f_ing:
                matching.append((f_ing, None))

    if not matching:
        return False, None, None

    desde, hasta = elegir_mejor_rango(matching, fecha_obj)
    return True, desde, hasta

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print(f"{Fore.WHITE}🚀 FRICKE IAM v2 — Hospitalización por fecha (con Desde/Hasta){Style.RESET_ALL}")

    # Conectar a Edge (9222)
    try:
        opts = webdriver.EdgeOptions()
        opts.debugger_address = DEBUG_PORT
        driver = webdriver.Edge(service=Service(EDGE_DRIVER_PATH), options=opts)
        print(f"{Fore.GREEN}Conectado a Edge en {DEBUG_PORT}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}No pude conectar a Edge (9222). ¿Abriste Edge con --remote-debugging-port=9222?{Style.RESET_ALL}")
        raise

    # Cargar Excel (Reporte → hoja IAM)
    try:
        df = pd.read_excel(RUTA_EXCEL_REPORTE, sheet_name=HOJA_IAM).iloc[1:].copy()
        print(f"{Fore.CYAN}Leí {len(df)} filas de '{os.path.basename(RUTA_EXCEL_REPORTE)}' / hoja '{HOJA_IAM}'{Style.RESET_ALL}\n")
    except Exception as e:
        print(f"{Fore.RED}No pude leer la hoja '{HOJA_IAM}': {e}{Style.RESET_ALL}")
        raise

    filas_salida = []
    for _, row in df.iterrows():
        # Extraer valores seguros
        rut = str(row.iloc[COL_RUT]).strip() if not pd.isna(row.iloc[COL_RUT]) else ""
        nombre = str(row.iloc[COL_NOMBRE]).strip() if (COL_NOMBRE is not None and not pd.isna(row.iloc[COL_NOMBRE])) else ""
        fecha_excel = parse_fecha_dmy(row.iloc[COL_FECHA]) if not pd.isna(row.iloc[COL_FECHA]) else None

        # Validación mínima
        if not rut or not fecha_excel:
            continue

        # Log por paciente (1 línea header + 1 línea resultado)
        log_header(nombre, rut, fecha_excel.strftime("%d/%m/%Y"))

        try:
            hosp, f_desde, f_hasta = buscar_rango_hosp(driver, rut, fecha_excel)
        except Exception as e:
            # En caso de error puntual, marcar No y seguir
            hosp, f_desde, f_hasta = False, None, None

        # Log resultado limpio
        log_result(hosp, fmt_dmy(f_desde), fmt_dmy(f_hasta))

        filas_salida.append({
            "Rut": rut,
            "Nombre": nombre,
            "Fecha": fecha_excel.strftime("%d/%m/%Y"),
            "Hospitalizado": "Sí" if hosp else "No",
            "Desde": fmt_dmy(f_desde),
            "Hasta": fmt_dmy(f_hasta),
        })

    # Guardar salida
    if filas_salida:
        os.makedirs(RUTA_CARPETA_SALIDA, exist_ok=True)
        out_file = os.path.join(
            RUTA_CARPETA_SALIDA,
            f"Revision_FRICKE_IAM_{datetime.now():%Y%m%d_%H%M}.xlsx"
        )
        pd.DataFrame(filas_salida).to_excel(out_file, index=False)
        print(f"{Fore.GREEN}Archivo generado: {out_file}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}No hubo filas para exportar.{Style.RESET_ALL}")

    print(f"{Fore.CYAN}Listo. Dejo el navegador abierto.{Style.RESET_ALL}")
