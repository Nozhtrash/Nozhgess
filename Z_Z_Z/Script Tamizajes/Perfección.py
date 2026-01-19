# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
from datetime import datetime
from colorama import Fore, Style, init as colorama_init
from collections import Counter
import time, openpyxl, sys, re, os

# ───────────────── Config ─────────────────
EMOJI_CLOCK = "⏰"; EMOJI_OK = "✅"; EMOJI_ERR = "❌"; EMOJI_RETRY = "🔁"; EMOJI_WARN = "⚠️"
AUTHOR = "Nozh"

SLEEP = 0.5               # pausa estándar en cada paso
PAUSE_AFTER_ADD = 2.0     # pausa tras agregar paciente
DUP_CHECK_EVERY = 50      # cada cuántos pacientes hacer chequeo de duplicados
CHECKPOINT_SLEEP_SEC = 10 # pausa humana antes de chequear duplicados (TR1..TR50)

URL_MASIVO = "https://www.sigges.cl/#/ingreso-de-prestaciones-otorgadas-integradas-masivas"
TXT_DIR = r"C:\Users\Usuario HGF\Desktop\Trabajo\Revisiones"

# Parametrización
CODIGO_PRESTACION = "0801101"
HORA_FIJA = "14:00"
PAUSA_POST_BUSCAR_RUN = 0.5
PAUSA_POST_DETECTAR_ACTIVAR = 0.5
DEBUG_NORMAL_MSG = False  # <<< si True, imprime "modo normal"

# Colores
colorama_init(autoreset=True)
C_CNT = Fore.MAGENTA; C_NAME = Fore.YELLOW; C_RUT = Fore.CYAN; C_DATE = Fore.LIGHTRED_EX
C_OK = Fore.GREEN; C_ERR = Fore.RED; C_DIM = Style.DIM

# Driver (depuración remota)
options = webdriver.EdgeOptions()
options.debugger_address = "localhost:9222"
driver = webdriver.Edge(service=Service(r"C:\Windows\System32\msedgedriver.exe"), options=options)

# ────────── XPaths base (pantalla original) ──────────
XPATH_CODIGO_INPUT = "/html/body/div/main/div[3]/div[2]/div/div[4]/div[2]/div[1]/div[1]/div/div[1]/div/input"
XPATH_BUSCAR_CODIGO = "/html/body/div/main/div[3]/div[2]/div/div[4]/div[2]/div[1]/div[1]/div/div[2]/button"
XPATH_LISTA_CODIGOS_FIRST = "/html/body/div/main/div[3]/div[2]/div/div[4]/div[2]/div[1]/div[2]/div/div/div[2]/div[1]"
XPATH_FECHA_INPUT = "/html/body/div/main/div[3]/div[2]/div/div[4]/div[4]/div[1]/div/div[1]/div/input"
XPATH_HORA_INPUT  = "/html/body/div/main/div[3]/div[2]/div/div[4]/div[4]/div[2]/div/div[2]/div/input"
XPATH_UNIDAD_SELECT = "/html/body/div/main/div[3]/div[2]/div/div[4]/div[5]/div[1]/div/select"
XPATH_UNIDAD_OPTION_2 = "/html/body/div/main/div[3]/div[2]/div/div[4]/div[5]/div[1]/div/select/option[2]"
XPATH_ESPECIALIDAD_SELECT = "/html/body/div/main/div[3]/div[2]/div/div[4]/div[5]/div[2]/div/select"
XPATH_ESPECIALIDAD_OPTION_92 = "/html/body/div/main/div[3]/div[2]/div/div[4]/div[5]/div[2]/div/select/option[92]"
XPATH_RUT_INPUT = "/html/body/div/main/div[3]/div[2]/div/div[6]/div[1]/div[1]/div[2]/input"
XPATH_BUSCAR_RUN = "/html/body/div/main/div[3]/div[2]/div/div[6]/div[1]/div[1]/button[1]"

# ORIGINAL (sin alerta)
XPATH_CASO_SELECT_ORIG = "/html/body/div/main/div[3]/div[2]/div/div[6]/div[2]/div[2]/div/select"
XPATH_ORDEN_ATENCION_ORIG = "/html/body/div/main/div[3]/div[2]/div/div[6]/div[3]/div/div[3]/div/label/div"
XPATH_FOLIO_SELECT_ORIG = "/html/body/div/main/div[3]/div[2]/div/div[6]/div[3]/div/div[5]/div/select"
XPATH_AGREGAR_PACIENTE_ORIG = "/html/body/div/main/div[3]/div[2]/div/div[6]/div[5]/div[1]/button"

# PARCHE (cuando aparece el aviso rojo)
XPATH_ALERTA_MULTI_PACIENTE_1 = "/html/body/div[1]/main/div[3]/div[2]/div/div[6]/div[1]/div/div/div/p"
XPATH_ALERTA_MULTI_PACIENTE_2 = "//div[@data-color='rojo']/p[contains(.,'El RUN especificado tiene más de un paciente asociado')]"
XPATH_CASO_SELECT_PATCH = "/html/body/div[1]/main/div[3]/div[2]/div/div[6]/div[3]/div[2]/div/select"
XPATH_ORDEN_ATENCION_PATCH = "/html/body/div[1]/main/div[3]/div[2]/div/div[6]/div[4]/div/div[3]/div/label/div"
XPATH_FOLIO_SELECT_PATCH = "/html/body/div/main/div[3]/div[2]/div/div[6]/div[4]/div/div[5]/div/select"
XPATH_AGREGAR_PACIENTE_PATCH = "/html/body/div[1]/main/div[3]/div[2]/div/div[6]/div[6]/div[1]/button"

# Tabla para verificación
XPATH_TBODY = "/html/body/div/main/div[3]/div[2]/div/div[6]/div[4]/div/table/tbody"

# Selectores para Spinner
SPINNER_SELECTORS = [
    (By.CSS_SELECTOR, "#root > dialog.loading > div"),
    (By.XPATH, "//*[@id='root']/dialog[2]/div"),
    (By.XPATH, "/html/body/div/dialog[2]/div"),
    (By.CSS_SELECTOR, "div.circulo")
]

# Entradas/Salidas
INPUT_EXCEL_PATH = r"C:\Users\Usuario HGF\Desktop\Trabajo\Tamizajes 29-10.xlsx"
RESULTS = []
DUP_CHECKPOINTS = []

# Estado del parche
parche_activo = False

# ─────────────── Helpers ───────────────
def ensure_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        print(f"{C_ERR}No se pudo crear/verificar carpeta {path}: {e}{Style.RESET_ALL}")

def short_error(e):
    t = type(e).__name__
    msg = str(e).splitlines()[0] if e else ""
    msg = msg[:120]; ml = msg.lower()
    if "interactable" in ml or "not interactable" in ml: return "Error de selección"
    if isinstance(e, TimeoutException) or "timeout" in ml: return "Timeout esperando elemento"
    if "no such element" in ml: return "Elemento no encontrado"
    if "stale" in ml: return "Elemento obsoleto (stale)"
    return f"{t}: {msg}"

def concise_print(idx, total, start_time, nombre, rut, fecha, status):
    linea = (f"{C_CNT}[{idx}/{total}]{Style.RESET_ALL} {start_time} | "
             f"{C_NAME}{nombre}{Style.RESET_ALL} | "
             f"{C_RUT}{rut}{Style.RESET_ALL} | "
             f"{C_DATE}{fecha}{Style.RESET_ALL} | {status}")
    print(linea)

def safe_click(el):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        el.click()
    except Exception:
        driver.execute_script("arguments[0].click();", el)

def slow_type(el, text, per_char=0.06, clear=True):
    if clear:
        el.clear(); time.sleep(0.1)
    for ch in str(text):
        el.send_keys(ch); time.sleep(per_char)

RUT_RGX = re.compile(r"(\d{1,2}\.?\d{3}\.?\d{3}-[0-9Kk])|(\d{7,8}-[0-9Kk])|(\d{7,9}[kK]?)")
DATE_RGX = re.compile(r"\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b")

def normalize_rut(s):
    return re.sub(r"[^0-9kK]", "", str(s))

def verify_patient_added(rut_normalizado):
    """True si el último rut coincide; None si no hay tabla; False si hay tabla y no coincide."""
    try:
        tbody = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, XPATH_TBODY)))
        last_rut = tbody.find_element(By.XPATH, "./tr[1]/td[4]").text
        return normalize_rut(last_rut) == rut_normalizado
    except TimeoutException:
        return None
    except Exception:
        return None

def is_spinner_visible():
    for by, sel in SPINNER_SELECTORS:
        try:
            el = driver.find_element(by, sel)
            if el and el.is_displayed():
                return True
        except Exception:
            continue
    return False

def wait_spinner_disappear(max_seconds=180):
    start = time.time()
    if not is_spinner_visible():
        return True
    while time.time() - start < max_seconds:
        if not is_spinner_visible():
            return True
        time.sleep(0.5)
    return False

def parse_table_rows(limit=None):
    pacientes = []
    try:
        tbody = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, XPATH_TBODY)))
    except Exception:
        return pacientes

    rows = tbody.find_elements(By.XPATH, "./tr")
    if limit:
        rows = rows[:limit]   # TR1..TRlimit

    for tr in rows:
        tds = tr.find_elements(By.TAG_NAME, "td")
        texts = [td.text.strip() for td in tds]

        rut, fecha, nombre = "", "", ""
        rut_idx, fecha_idx = -1, -1

        for idx, txt in enumerate(texts):
            if not rut and RUT_RGX.search(txt):
                rut, rut_idx = txt, idx
                break
        for idx, txt in enumerate(texts):
            if DATE_RGX.search(txt):
                fecha, fecha_idx = txt, idx
                break

        for idx, txt in enumerate(texts):
            if idx in (rut_idx, fecha_idx):
                continue
            if re.search(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]{2,}", txt):
                nombre = txt
                break

        if not rut and len(texts) >= 4: rut = texts[3]
        if not nombre and len(texts) >= 2: nombre = texts[1]
        if not fecha and len(texts) >= 3: fecha = texts[2]

        pacientes.append({"Rut": rut, "Nombre": nombre, "Fecha": fecha})
    return pacientes

def scan_table_for_duplicates(limit=None):
    rows = parse_table_rows(limit=limit)
    key_counts = Counter((normalize_rut(r["Rut"]), r["Fecha"]) for r in rows if r["Rut"])
    dups_keys = {k for k, c in key_counts.items() if c > 1}
    duplicates = []
    if dups_keys:
        seen = set()
        for r in rows:
            key = (normalize_rut(r["Rut"]), r["Fecha"])
            if key in dups_keys and key not in seen:
                duplicates.append({"Rut": r["Rut"], "Nombre": r["Nombre"], "Fecha": r["Fecha"]})
                seen.add(key)
    return duplicates

def write_revision_txt(total, ok_cnt, notok_cnt, not_verified_list, checkpoints, final_duplicates):
    ensure_dir(TXT_DIR)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    txt_name = f"Revision Tamizajes {timestamp}.txt"
    txt_path = os.path.join(TXT_DIR, txt_name)

    try:
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("===== REVISIÓN DE TAMIZAJES =====\n")
            f.write(f"Fecha/Hora: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n")
            f.write(f"Fuente Excel: {INPUT_EXCEL_PATH}\n\n")

            f.write("— PACIENTES NO VERIFICADOS EN LA TABLA —\n")
            if not not_verified_list:
                f.write("No hay pacientes 'No Verificados en la Tabla'.\n\n")
            else:
                f.write("Rut | Nombre | Fecha\n")
                for r in not_verified_list:
                    f.write(f"{r['Rut']} | {r['Nombre']} | {r['Fecha']}\n")
                f.write("\n")

            f.write("— RESUMEN —\n")
            f.write(f"De {total} pacientes, {ok_cnt} se hicieron bien y {notok_cnt} no fueron verificados en la tabla.\n\n")

            f.write("— CHEQUEOS DE DUPLICADOS (cada 50, TR1..TR50) —\n")
            if not checkpoints:
                f.write("No se realizaron chequeos intermedios o no había tabla.\n\n")
            else:
                for snap in checkpoints:
                    f.write(f"Tras {snap['after']} pacientes → Duplicados hallados: {len(snap['duplicates'])} (alcance: {snap.get('scope','TR1..TR50')})\n")
                    if snap['duplicates']:
                        f.write("Rut | Nombre | Fecha\n")
                        for r in snap['duplicates']:
                            f.write(f"{r['Rut']} | {r['Nombre']} | {r['Fecha']}\n")
                    f.write("\n")

            f.write("— DUPLICADOS AL FINAL (toda la tabla) —\n")
            f.write(f"Se encontraron {len(final_duplicates)} pacientes duplicados (clave: RUT+Fecha).\n")
            if final_duplicates:
                f.write("Rut | Nombre | Fecha\n")
                for r in final_duplicates:
                    f.write(f"{r['Rut']} | {r['Nombre']} | {r['Fecha']}\n")
            f.write("\n")

        print(f"{C_OK}TXT de revisión guardado en: {txt_path}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{C_ERR}No se pudo escribir el TXT de revisión: {e}{Style.RESET_ALL}")

def save_results_excel():
    try:
        wb_out = openpyxl.Workbook()
        ws = wb_out.active; ws.title = "Verificación"
        ws.append(["Rut", "Nombre", "Fecha", "Observación"])
        for r in RESULTS:
            ws.append([r["Rut"], r["Nombre"], r["Fecha"], r["Observación"]])
        base = os.path.basename(INPUT_EXCEL_PATH)
        root, ext = os.path.splitext(base)
        out_name = f"{root} Verificación{ext}"
        out_path = os.path.join(os.path.dirname(INPUT_EXCEL_PATH), out_name)
        wb_out.save(out_path)
        print(f"{C_OK}Archivo de verificación guardado en: {out_path}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{C_ERR}No se pudo guardar el Excel de verificación: {e}{Style.RESET_ALL}")

# ─────────────── Utilidades del PARCHE ───────────────
def alerta_multi_paciente_presente(timeout=2):
    """Detecta el aviso rojo 'El RUN especificado tiene más de un paciente asociado'."""
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, XPATH_ALERTA_MULTI_PACIENTE_1))
        )
        if el and "más de un paciente" in (el.text or ""):
            return True
    except Exception:
        pass
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, XPATH_ALERTA_MULTI_PACIENTE_2))
        )
        return el is not None
    except Exception:
        return False

def wait_clickable_first_match(xpaths, timeout_each=6):
    """Devuelve el primer elemento clickable probando una lista de XPaths en orden."""
    last_exc = None
    for xp in xpaths:
        try:
            return WebDriverWait(driver, timeout_each).until(EC.element_to_be_clickable((By.XPATH, xp)))
        except Exception as e:
            last_exc = e
            continue
    if last_exc:
        raise last_exc
    raise TimeoutException("Ninguno de los XPaths fue clickable.")

def get_xpaths_for(name, prefer_patch=None):
    """
    Devuelve lista ordenada de XPaths para 'caso', 'orden', 'folio', 'agregar'.
    prefer_patch: True -> prioriza patch; False -> prioriza original; None -> orig primero.
    """
    if name == "caso":
        orig = XPATH_CASO_SELECT_ORIG; patch = XPATH_CASO_SELECT_PATCH
    elif name == "orden":
        orig = XPATH_ORDEN_ATENCION_ORIG; patch = XPATH_ORDEN_ATENCION_PATCH
    elif name == "folio":
        orig = XPATH_FOLIO_SELECT_ORIG; patch = XPATH_FOLIO_SELECT_PATCH
    elif name == "agregar":
        orig = XPATH_AGREGAR_PACIENTE_ORIG; patch = XPATH_AGREGAR_PACIENTE_PATCH
    else:
        raise ValueError("name inválido")

    if prefer_patch is True:
        return [patch, orig]
    if prefer_patch is False:
        return [orig, patch]
    return [orig, patch]

def choose_first_valid_option(select_el):
    """Elige la primera opción válida (no disabled, value != '0')."""
    WebDriverWait(driver, 10).until(lambda d: len(select_el.find_elements(By.TAG_NAME, "option")) >= 1)
    options = select_el.find_elements(By.TAG_NAME, "option")
    for opt in options:
        if opt.get_attribute("disabled"):
            continue
        val = (opt.get_attribute("value") or "").strip()
        if val and val != "0":
            return opt
    return None

# ─────────────── Acciones modularizadas ───────────────
def seleccionar_codigo():
    codigo_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATH_CODIGO_INPUT)))
    slow_type(codigo_input, CODIGO_PRESTACION, per_char=0.05); time.sleep(SLEEP)

    buscar_codigo = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATH_BUSCAR_CODIGO)))
    safe_click(buscar_codigo); time.sleep(SLEEP)

    proc = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATH_LISTA_CODIGOS_FIRST)))
    safe_click(proc); time.sleep(SLEEP)

def set_fecha_hora(fecha_val):
    time.sleep(SLEEP)
    fecha_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATH_FECHA_INPUT)))
    fecha_input.clear(); fecha_input.send_keys(fecha_val)
    time.sleep(SLEEP)

    hora_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATH_HORA_INPUT)))
    hora_input.clear(); hora_input.send_keys(HORA_FIJA)
    time.sleep(SLEEP)

def seleccionar_unidad_especialidad():
    unidad_select = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATH_UNIDAD_SELECT)))
    safe_click(unidad_select); time.sleep(SLEEP)
    unidad_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATH_UNIDAD_OPTION_2)))
    safe_click(unidad_option); time.sleep(SLEEP)

    especialidad_select = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATH_ESPECIALIDAD_SELECT)))
    safe_click(especialidad_select); time.sleep(SLEEP)
    especialidad_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATH_ESPECIALIDAD_OPTION_92)))
    safe_click(especialidad_option); time.sleep(SLEEP)

def ingresar_run_y_caso(rut_norm):
    """Ingresa RUN, busca, detecta alerta y selecciona el caso con el XPath que corresponda.
       Timings:
         - después de Buscar RUN => sleep(0.5)
         - antes del detector => sleep(1.0)
         - si detecta => sleep(0.5) antes de activar parche
    """
    global parche_activo

    rut_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATH_RUT_INPUT)))
    slow_type(rut_input, rut_norm, per_char=0.04); time.sleep(SLEEP)

    buscar_run = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATH_BUSCAR_RUN)))
    safe_click(buscar_run)

    time.sleep(PAUSA_POST_BUSCAR_RUN)

    parche_activo = alerta_multi_paciente_presente(timeout=1.0)
    if parche_activo:
        time.sleep(PAUSA_POST_DETECTAR_ACTIVAR)
        print("🟥 Aviso rojo: RUN con múltiples pacientes. Activando PARCHE para 'Caso/Orden/Folio/Agregar'.")
    else:
        if DEBUG_NORMAL_MSG:
            print("🟩 Sin alerta de múltiples pacientes. Modo normal.")

    # Selección de caso (probando XPaths según el estado del parche, con fallback)
    prefer = True if parche_activo else False
    caso_select = wait_clickable_first_match(get_xpaths_for("caso", prefer_patch=prefer))
    time.sleep(SLEEP)

    caso_encontrado = False
    for opt in caso_select.find_elements(By.TAG_NAME, 'option'):
        txt = (opt.text or "")
        if "Cáncer Cervicouterino Segmento Proceso de Diagnóstico" in txt and "Caso en Sospecha" in txt:
            opt.click(); caso_encontrado = True; break
    if not caso_encontrado:
        for opt in caso_select.find_elements(By.TAG_NAME, 'option'):
            txt = (opt.text or "")
            if "Cáncer Cervicouterino Segmento Proceso de Diagnóstico" in txt and "Caso Cerrado" in txt:
                opt.click(); caso_encontrado = True; break
    if not caso_encontrado:
        raise Exception("No se encontró caso apropiado")
    time.sleep(SLEEP)

def seleccionar_orden_y_folio():
    """Marca 'Orden de atención' y elige el primer folio válido. Usa parche si está activo."""
    prefer = True if parche_activo else False

    # Orden de atención
    orden_atencion = wait_clickable_first_match(get_xpaths_for("orden", prefer_patch=prefer))
    safe_click(orden_atencion); time.sleep(SLEEP)

    # Folio (normal vs parche)
    folio_select = wait_clickable_first_match(get_xpaths_for("folio", prefer_patch=prefer))
    safe_click(folio_select); time.sleep(SLEEP)

    # Elegir la primera opción válida
    opt = choose_first_valid_option(folio_select)
    if not opt:
        raise Exception("No hay folios válidos")
    safe_click(opt); time.sleep(SLEEP)

def agregar_y_verificar(rut_norm):
    """Click en 'Agregar paciente' con el XPath correspondiente y verificación en tabla."""
    global parche_activo
    prefer = True if parche_activo else False

    agregar_paciente = wait_clickable_first_match(get_xpaths_for("agregar", prefer_patch=prefer))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", agregar_paciente)
    safe_click(agregar_paciente)
    time.sleep(PAUSE_AFTER_ADD)

    # Desactivar parche tras agregar
    if parche_activo:
        parche_activo = False  # silencioso (sin spam)
    return verify_patient_added(rut_norm)  # True/False/None

# ─────────────── Inicio ───────────────
print(f"{EMOJI_CLOCK} Script de Tamizajes iniciando... Hecho por {AUTHOR} {EMOJI_CLOCK}")

driver.get(URL_MASIVO)
try:
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "/html/body/div/main/div[2]/nav/div[2]")))
except Exception:
    print(f"{EMOJI_WARN} No se detectó la página principal. Revisa la sesión de Edge en depuración.")
    raise

# Excel
wb = openpyxl.load_workbook(INPUT_EXCEL_PATH)
sheet = wb.active
rows = list(sheet.iter_rows(min_row=2, values_only=True))
valid_rows = [r for r in rows if r and r[0]]
total = len(valid_rows)
if total == 0:
    print("❌ No se encontraron pacientes en el Excel (columna RUT vacía)."); sys.exit(0)

ok_cnt, notok_cnt = 0, 0

# ─────────────── Bucle ───────────────
for i, row in enumerate(valid_rows, start=1):
    rut_raw = str(row[0]); rut_norm = normalize_rut(rut_raw)
    nombre = row[1] if row[1] else "SIN_NOMBRE"
    try:
        fecha_val = row[2].strftime("%d-%m-%Y") if hasattr(row[2], "strftime") else (str(row[2]) if row[2] else "SIN_FECHA")
    except Exception:
        fecha_val = "SIN_FECHA"

    start_time = datetime.now().strftime("%H:%M:%S")
    concise_print(i, total, start_time, nombre, rut_raw, fecha_val, "Iniciando...")

    intentos, max_intentos = 0, 4
    while True:
        try:
            seleccionar_codigo()
            set_fecha_hora(fecha_val)
            seleccionar_unidad_especialidad()
            ingresar_run_y_caso(rut_norm)
            seleccionar_orden_y_folio()
            verif = agregar_y_verificar(rut_norm)

            if verif is True:
                concise_print(i, total, start_time, nombre, rut_raw, fecha_val,
                              f"{C_OK}Ingresado y confirmado en lista {EMOJI_OK}{Style.RESET_ALL}")
                RESULTS.append({"Rut": rut_raw, "Nombre": nombre, "Fecha": fecha_val, "Observación": "Verificado en la Tabla"})
                ok_cnt += 1
                break
            elif verif is None:
                concise_print(i, total, start_time, nombre, rut_raw, fecha_val,
                              f"{C_OK}Agregado, lista vacía/no presente → No Verificado en la Tabla 🟡{Style.RESET_ALL}")
                RESULTS.append({"Rut": rut_raw, "Nombre": nombre, "Fecha": fecha_val, "Observación": "No Verificado en la Tabla"})
                notok_cnt += 1
                break
            else:
                concise_print(i, total, start_time, nombre, rut_raw, fecha_val,
                              f"{C_ERR}Último paciente no coincide (No Verificado en la Tabla). Se continúa.{Style.RESET_ALL}")
                RESULTS.append({"Rut": rut_raw, "Nombre": nombre, "Fecha": fecha_val, "Observación": "No Verificado en la Tabla"})
                notok_cnt += 1
                break

        except Exception as e:
            intentos += 1
            err_label = short_error(e)

            if intentos < max_intentos:
                concise_print(i, total, start_time, nombre, rut_raw, fecha_val,
                              f"{C_ERR}Error: {err_label}{Style.RESET_ALL} {EMOJI_RETRY} ({intentos}/{max_intentos})")
                time.sleep(8)

                if intentos == 3:
                    # 1) Intentar cerrar pop-up si existe
                    try:
                        XPATH_POPUP_BOTON_OK = "/html/body/div/main/div[3]/div[2]/div/dialog[6]/div[3]/button"
                        boton_aceptar = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, XPATH_POPUP_BOTON_OK)))
                        safe_click(boton_aceptar); time.sleep(SLEEP)
                    except Exception:
                        pass
                    # 2) Verificar spinner (hasta 3 minutos). Si no se va, refrescar URL
                    if is_spinner_visible():
                        print(f"{EMOJI_WARN} Spinner detectado. Esperando hasta 3 minutos…")
                        if wait_spinner_disappear(180):
                            time.sleep(1)
                        else:
                            print(f"{EMOJI_WARN} Spinner no se fue en 3 minutos. Refrescando…")
                            driver.get(URL_MASIVO); time.sleep(5)
                continue
            else:
                concise_print(i, total, start_time, nombre, rut_raw, fecha_val,
                              f"{C_ERR}Falló: {err_label}{Style.RESET_ALL} {EMOJI_ERR}")
                user_choice = input("Enter = REINTENTAR este paciente | '*' + Enter = SALTARlo | 'q' + Enter = Salir: ").strip().lower()
                if user_choice == "*":
                    concise_print(i, total, start_time, nombre, rut_raw, fecha_val, "Saltado por usuario ⏭️")
                    RESULTS.append({"Rut": rut_raw, "Nombre": nombre, "Fecha": fecha_val, "Observación": "No Verificado en la Tabla"})
                    notok_cnt += 1
                    break
                elif user_choice == "q":
                    print("⛔ Salida solicitada. Guardando resultados…")
                    final_dups = scan_table_for_duplicates()  # full
                    not_verified = [r for r in RESULTS if r["Observación"] == "No Verificado en la Tabla"]
                    write_revision_txt(total, ok_cnt, notok_cnt, not_verified, DUP_CHECKPOINTS, final_dups)
                    save_results_excel()
                    print(f"{C_OK}Resumen → Verificados: {ok_cnt} | No Verificados: {notok_cnt}{Style.RESET_ALL}")
                    sys.exit(0)
                else:
                    intentos = 0
                    concise_print(i, total, start_time, nombre, rut_raw, fecha_val, f"{C_DIM}Reintentando manualmente…{Style.RESET_ALL}")
                    time.sleep(5)
                    continue

    # ── Chequeo de duplicados cada 50 ──
    if i % DUP_CHECK_EVERY == 0 and i < total:
        try:
            print(f"⏸️ Pausa de {CHECKPOINT_SLEEP_SEC}s para revisión humana (TR1..TR50)…")
            time.sleep(CHECKPOINT_SLEEP_SEC)
            dups_top50 = scan_table_for_duplicates(limit=50)
            DUP_CHECKPOINTS.append({"after": i, "duplicates": dups_top50, "scope": "TR1..TR50"})
            if dups_top50:
                print(f"{EMOJI_WARN} Duplicados tras {i}: {len(dups_top50)} (TR1..TR50).")
                for d in dups_top50:
                    print(f"  - {d['Rut']} | {d['Nombre']} | {d['Fecha']}")
            else:
                print(f"🧹 Sin duplicados tras {i} (TR1..TR50).")
        except Exception as e:
            print(f"{C_ERR}Error al escanear duplicados tras {i}: {e}{Style.RESET_ALL}")

# Fin: guardados y resumen
final_dups = scan_table_for_duplicates()
not_verified = [r for r in RESULTS if r["Observación"] == "No Verificado en la Tabla"]
write_revision_txt(total, ok_cnt, notok_cnt, not_verified, DUP_CHECKPOINTS, final_dups)
save_results_excel()

print(f"{C_OK}Resumen → Verificados: {ok_cnt} | No Verificados: {notok_cnt}{Style.RESET_ALL}")
print("🏁 Proceso terminado.")
