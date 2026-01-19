# -*- coding: utf-8 -*-
import os
import re
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from colorama import Fore, Style, init
import unicodedata

# =================================================================================
# 🎮 PANEL DE CONTROL OMEGA – CONFIGURA TU MISIÓN AQUÍ
# =================================================================================

# Nombre que tendrá el reporte final y el archivo XLSX de salida.
NOMBRE_DE_LA_MISION = "Prevencion Parto"

# Ruta del Excel de entrada con los pacientes a revisar.
# Debe contener las columnas de fecha, RUT y nombre en las posiciones indicadas
RUTA_ARCHIVO_ENTRADA = r"C:\\Users\\Usuario HGF\\Desktop\\Trabajo\\Obstetricia.xlsx"

# Carpeta donde se guardará el informe final generado.
RUTA_CARPETA_SALIDA = r"C:\\Users\\Usuario HGF\\Desktop\\Trabajo\\Extra\\Revisiones"

# Lista de misiones a ejecutar. Cada misión representa un código que queremos buscar
# dentro de los casos activos del paciente. Si detener_al_exito es True, el script
# dejará de buscar más misiones para ese paciente en cuanto encuentre la actual.
SECUENCIA_DE_MISIONES = [
    {
        "nombre_mision": "Prevencion Parto",
        "keywords_caso": ["prematurez prevención parto prematuro", "prematurez prevencion parto prematuro", "parto prematuro"],
        "codigo_requerido": "3114103",   # Seguimiento a digitar (chequeo de duplicado)
        "detener_al_exito": False
    },
    {
        "nombre_mision": "Prevencion Parto",
        "keywords_caso": ["prematurez prevención parto prematuro", "prematurez prevencion parto prematuro", "parto prematuro"],
        "codigo_requerido": "3114101",   # Habilitante 1
        "detener_al_exito": False
    },
    {
        "nombre_mision": "Prevencion Parto",
        "keywords_caso": ["prematurez prevención parto prematuro", "prematurez prevencion parto prematuro", "parto prematuro"],
        "codigo_requerido": "3114102",   # Habilitante 2
        "detener_al_exito": True
    },
]

# Índices de las columnas en el Excel de entrada: fecha, RUT y nombre (base 0)
INDICE_COLUMNA_FECHA = 0
INDICE_COLUMNA_RUT   = 2
INDICE_COLUMNA_NOMBRE= 4

# Datos de conexión al WebDriver de Edge en modo debug
DIRECCION_DEBUG_EDGE = "localhost:9222"
EDGE_DRIVER_PATH     = r"C:\\Windows\\System32\\msedgedriver.exe"

# Número máximo de reintentos por paciente.
MAXIMOS_REINTENTOS_POR_PACIENTE = 3

# ============================ FIN DEL PANEL DE CONTROL ==============================

# Inicializamos colorama para tener textos con colores en la consola
init(autoreset=True)
EMOJI_OK, EMOJI_NO, EMOJI_WARN = "✅", "❌", "⚠️"
EMOJI_START, EMOJI_CASE, EMOJI_CODE, EMOJI_SPINNER = "🚀", "📋", "💉", "🌀"
EMOJI_STOP, EMOJI_ROBOT, EMOJI_SKULL = "🛑", "🤖", "💀"

def log(tipo: str, mensaje: str) -> None:
    """Imprime mensajes de log con colores y emojis según el tipo."""
    colores = {
        "exito": Fore.GREEN,
        "error": Fore.RED,
        "info": Fore.CYAN,
        "warn": Fore.YELLOW,
        "debug": Fore.MAGENTA
    }
    emojis = {
        "exito": EMOJI_OK,
        "error": EMOJI_NO,
        "info": EMOJI_ROBOT,
        "warn": EMOJI_WARN,
        "debug": EMOJI_SKULL
    }
    print(f"{colores.get(tipo, Fore.WHITE)}{emojis.get(tipo, '')} {mensaje}{Style.RESET_ALL}")

# Selector del spinner de carga. Se espera hasta que desaparezca para continuar.
CSS_SELECTOR_SPINNER = "dialog.loading"

# Lista de estados que consideramos como casos activos o en evaluación
ESTADOS_ACTIVOS = [
    "caso confirmado", "caso activo", "caso en tratamiento",
    "caso en sospecha", "caso en seguimiento", "caso con estudio de pre-transplante",
    "caso en proceso de diagnóstico", "tratamiento"
]

# XPaths de la interfaz de SIGGES. (mismos del script base)
XPATH_RUT              = "/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/div/div/input"
XPATH_BTN_BUSCAR       = "/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/button/p"
XPATH_CARTOLA          = "/html/body/div/main/div[2]/nav/div[1]/div[2]/a[4]/p"
XPATH_CHECKBOX_HITOS   = "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div/div/label/input"
XPATH_LISTA_CASOS_ROOT = "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]"
XPATH_BTN_INICIO       = "/html/body/div/main/div[2]/nav/div[1]/div[2]/a[1]/p"

# Columnas (índices) dentro de la tabla de prestaciones
COL_FECHA_DIGITACION  = 2
COL_CODIGO_PRESTACION = 7

def _normalize_text(s: str) -> str:
    """Pasa a minúsculas y elimina tildes."""
    s = s or ""
    s = s.lower()
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def get_xpath_caso_n(idx: int) -> str:
    """XPath del contenedor del caso en la posición dada (base 1)."""
    return f"{XPATH_LISTA_CASOS_ROOT}/div[{idx}]"

def get_xpath_checkbox_caso_n(idx: int) -> str:
    """XPath del checkbox para desplegar/cerrar un caso (base 1)."""
    return f"{get_xpath_caso_n(idx)}/div/label/input"

def get_xpath_tabla_prestaciones_caso_n(idx: int) -> str:
    """XPath de la tabla de prestaciones del caso desplegado."""
    return f"{get_xpath_caso_n(idx)}/div[6]/div[2]/div/table"

def get_xpath_tbody_prestaciones_caso_n(idx: int) -> str:
    """XPath del cuerpo (tbody) de la tabla de prestaciones."""
    return f"{get_xpath_tabla_prestaciones_caso_n(idx)}/tbody"

def esperar_a_que_cargue(driver: webdriver.Edge, timeout: int = 30) -> bool:
    """Espera hasta que desaparezca el spinner de carga. Devuelve True si carga bien."""
    try:
        WebDriverWait(driver, timeout).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, CSS_SELECTOR_SPINNER)))
        time.sleep(1)
        return True
    except TimeoutException:
        log("error", f"El sistema se quedó pegado esperando la carga {EMOJI_SPINNER}.")
        return False

def esperar_elemento(driver: webdriver.Edge, xpath: str, timeout: int = 15):
    """Devuelve el elemento clickable si aparece dentro del timeout, o None."""
    try:
        return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    except TimeoutException:
        log("warn", f"No se encontró el elemento esperado: {xpath}")
        return None

def solo_fecha(dt) -> str:
    """Convierte cualquier fecha (datetime, string, etc.) a formato dd/mm/yyyy."""
    if isinstance(dt, datetime):
        return dt.strftime("%d/%m/%Y")
    s = str(dt).split(' ')[0].replace('-', '/')
    parts = s.split('/')
    # Si el formato es yyyy/mm/dd lo invertimos
    if len(parts) >= 3 and len(parts[0]) == 4:
        return f"{parts[2]}/{parts[1]}/{parts[0]}"
    return s

def _extraer_fecha_ddmmyyyy(texto: str):
    """
    Busca la primera fecha dd/mm/yyyy en el texto del caso.
    Retorna (fecha_str, anio_int) o ("N/A", None)
    """
    m = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
    if not m:
        return "N/A", None
    fs = m.group(1)
    try:
        y = int(fs[-4:])
    except:
        y = None
    return fs, y

def _clasificar_antiguedad(fecha_excel_ddmmyyyy: str, fecha_caso_ddmmyyyy: str) -> str:
    """
    Regla solicitada por Nozh:
      - 2–3 años  -> "Nuevo"
      - ≤1 año    -> "Viejo"
      - >3 años   -> "Antiguo"
      - sin fecha -> "Sin fecha"
    """
    if fecha_caso_ddmmyyyy == "N/A":
        return "Sin fecha"
    try:
        fe = datetime.strptime(fecha_excel_ddmmyyyy, "%d/%m/%Y")
        fc = datetime.strptime(fecha_caso_ddmmyyyy, "%d/%m/%Y")
        dias = abs((fe - fc).days)
        anios = dias / 365.0
        if 2.0 <= anios <= 3.0:
            return "Nuevo (2–3 años)"
        elif anios <= 1.0:
            return "Viejo (≤1 año)"
        elif anios > 3.0:
            return "Antiguo (>3 años)"
        else:
            # 1–2 años (zona gris): tratamos como Viejo para ser estrictos
            return "Viejo (≤1 año)"
    except Exception:
        return "Sin fecha"

def revisar_prestaciones(driver: webdriver.Edge, idx_caso: int, codigo_requerido: str, fecha_excel: str):
    """
    Busca dentro de la tabla de prestaciones si existe un código específico y en qué fecha se digitó.
    Devuelve dict con { codigo_encontrado, fecha_digitacion, misma_fecha }.
    """
    resultado = {"codigo_encontrado": None, "fecha_digitacion": "N/A", "misma_fecha": "N/A"}

    if not codigo_requerido:
        return resultado

    try:
        tbody = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, get_xpath_tbody_prestaciones_caso_n(idx_caso)))
        )
        filas = tbody.find_elements(By.TAG_NAME, "tr")
        # Recorremos de más reciente a más antiguo
        for fila in reversed(filas):
            cols = fila.find_elements(By.TAG_NAME, "td")
            if len(cols) > COL_CODIGO_PRESTACION:
                fecha_completa = cols[COL_FECHA_DIGITACION].text.strip()
                codigo_actual  = cols[COL_CODIGO_PRESTACION].text.strip()
                fecha_sola = fecha_completa.split(' ')[0]
                if codigo_actual == codigo_requerido:
                    resultado["codigo_encontrado"] = codigo_actual
                    resultado["fecha_digitacion"] = fecha_sola
                    resultado["misma_fecha"] = "Sí" if fecha_sola == fecha_excel else "No"
                    if resultado["misma_fecha"] == "Sí":
                        log("exito", f"Código {codigo_requerido} encontrado el {fecha_sola} (coincide con Excel)")
                    else:
                        log("warn", f"Código {codigo_requerido} encontrado el {fecha_sola}, no coincide con Excel ({fecha_excel})")
                    return resultado
    except Exception as e:
        log("error", f"Error al revisar prestaciones: {e} 🐛")
    return resultado

def analizar_paciente(driver: webdriver.Edge, nombre: str, rut: str, fecha_excel: str):
    """
    Analiza un paciente: busca el caso de Prematurez – Prevención Parto Prematuro,
    determina antigüedad del caso, revisa 3114101, 3114102 y 3114103 (duplicado) y decide Apto.
    """
    resultado = {
        "Fecha": fecha_excel,
        "Rut": rut,
        "Nombre": nombre,
        "Información Adicional": ""
    }

    # Inicializa columnas por misión (formato del script base)
    for m in SECUENCIA_DE_MISIONES:
        codigo = m['codigo_requerido']
        resultado[f"Misión {codigo}"] = "Sin caso"
        resultado[f"Encontrada {codigo}"] = "N/A"
        resultado[f"Misma Fecha {codigo}"] = "N/A"

    # Campos extra
    resultado["Año Creación Caso"] = "N/A"
    resultado["Antigüedad Caso"]  = "Sin fecha"
    resultado["Apto para 3114103"] = "No"

    try:
        driver.get("https://nuevo.sigges.cl/#/busqueda-de-paciente")
        if not esperar_a_que_cargue(driver):
            return resultado

        inp = esperar_elemento(driver, XPATH_RUT)
        if not inp:
            return resultado
        inp.clear()
        inp.send_keys(rut)

        btn = esperar_elemento(driver, XPATH_BTN_BUSCAR)
        if not btn:
            return resultado
        btn.click()
        if not esperar_a_que_cargue(driver):
            return resultado

        btn_cartola = esperar_elemento(driver, XPATH_CARTOLA)
        if not btn_cartola:
            return resultado
        btn_cartola.click()
        if not esperar_a_que_cargue(driver):
            return resultado

        chk_hitos = esperar_elemento(driver, XPATH_CHECKBOX_HITOS)
        if chk_hitos:
            try:
                chk_hitos.click()
                esperar_a_que_cargue(driver)
            except Exception:
                pass

        lista_casos = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, XPATH_LISTA_CASOS_ROOT))
        )
        casos_divs = lista_casos.find_elements(By.CSS_SELECTOR, "div.contRow")

        # Normalizamos textos y comparamos con keywords TAL CUAL definiste (simple "any")
        casos_texto = [_normalize_text(c.text) for c in casos_divs]
        keywords_llano = [_normalize_text(k) for m in SECUENCIA_DE_MISIONES for k in m["keywords_caso"]]
        keywords_llano = list(dict.fromkeys(keywords_llano))  # únicos

        # Buscar el primer caso activo cuyo texto contenga cualquiera de los keywords
        idx_target = None
        estado_detectado = None
        texto_raw_elegido = ""

        for i, cdiv in enumerate(casos_divs):
            texto_norm = casos_texto[i]
            is_active = any(est in texto_norm for est in ESTADOS_ACTIVOS)
            if not is_active:
                continue
            if any(kw in texto_norm for kw in keywords_llano):
                idx_target = i + 1
                texto_raw_elegido = cdiv.text
                estado_detectado = next((est for est in ESTADOS_ACTIVOS if est in texto_norm), None)
                break

        if not idx_target:
            resultado["Información Adicional"] = "No se encontró caso de Prematurez Prevención Parto Prematuro."
            return resultado

        # Extraer fecha de creación del caso y clasificar antigüedad
        fecha_caso, anio_creacion = _extraer_fecha_ddmmyyyy(texto_raw_elegido)
        resultado["Año Creación Caso"] = str(anio_creacion) if anio_creacion else "N/A"
        resultado["Antigüedad Caso"]   = _clasificar_antiguedad(fecha_excel, fecha_caso)

        # Marcar estado del caso en cada misión
        if estado_detectado:
            for m in SECUENCIA_DE_MISIONES:
                codigo = m['codigo_requerido']
                resultado[f"Misión {codigo}"] = estado_detectado.title()

        # Desplegar acordeón
        chk_xpath = get_xpath_checkbox_caso_n(idx_target)
        chk = esperar_elemento(driver, chk_xpath)
        if chk:
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", chk)
                try:
                    chk.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", chk)
                esperar_a_que_cargue(driver)
            except Exception:
                pass

            # Ejecutar misiones (3114103, 3114101, 3114102)
            for m in SECUENCIA_DE_MISIONES:
                codigo = m["codigo_requerido"]
                verif = revisar_prestaciones(driver, idx_target, codigo, fecha_excel)
                resultado[f"Encontrada {codigo}"]  = verif['fecha_digitacion']
                resultado[f"Misma Fecha {codigo}"] = verif['misma_fecha']

            # Cerrar acordeón (best effort)
            try:
                chk2 = esperar_elemento(driver, chk_xpath)
                if chk2:
                    try:
                        chk2.click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", chk2)
                    esperar_a_que_cargue(driver)
            except Exception:
                pass

        # Lógica Apto para 3114103:
        # - Debe tener 3114101 y 3114102 (encontrados en cualquier fecha)
        # - 3114103 NO debe estar el mismo día que la fecha del Excel
        tiene_4101 = resultado.get("Encontrada 3114101", "N/A") != "N/A"
        tiene_4102 = resultado.get("Encontrada 3114102", "N/A") != "N/A"
        fecha_4103 = resultado.get("Encontrada 3114103", "N/A")
        dup_4103   = (fecha_4103 != "N/A") and (resultado.get("Misma Fecha 3114103") == "Sí")

        apto = (tiene_4101 and tiene_4102 and not dup_4103)
        resultado["Apto para 3114103"] = "Sí" if apto else "No"

        # Información adicional: año + etiqueta de antigüedad
        resultado["Información Adicional"] = f"Año de creación del caso: {resultado['Año Creación Caso']} ({resultado['Antigüedad Caso']})"

    except Exception as e:
        log("error", f"Error general al revisar al paciente {nombre}: {e}")

    return resultado

def ejecutar_revision():
    """
    Función principal que ejecuta la revisión para todos los pacientes del archivo de entrada
    y genera un reporte en Excel con los resultados.
    """
    log("info", f"{EMOJI_START} Iniciando revisión: {NOMBRE_DE_LA_MISION}")
    try:
        options = webdriver.EdgeOptions()
        options.debugger_address = DIRECCION_DEBUG_EDGE
        driver = webdriver.Edge(service=Service(EDGE_DRIVER_PATH), options=options)
        log("exito", "Conectado correctamente al navegador Edge en modo debug.")
    except WebDriverException as e:
        log("error", f"No se pudo conectar con Edge: {e}")
        return

    try:
        df = pd.read_excel(RUTA_ARCHIVO_ENTRADA)
        log("info", f"Archivo cargado: {RUTA_ARCHIVO_ENTRADA} con {len(df)} pacientes.")
    except Exception as e:
        log("error", f"No se pudo leer el archivo Excel: {e}")
        return

    resultados = []
    for index, row in df.iterrows():
        nombre = str(row.iloc[INDICE_COLUMNA_NOMBRE]).strip()
        rut = str(row.iloc[INDICE_COLUMNA_RUT]).strip()
        fecha_excel = solo_fecha(row.iloc[INDICE_COLUMNA_FECHA])

        result_paciente = None
        for intento in range(1, MAXIMOS_REINTENTOS_POR_PACIENTE + 1):
            try:
                log("info", f"Procesando paciente {nombre} (RUT: {rut}) – Intento {intento}")
                result_paciente = analizar_paciente(driver, nombre, rut, fecha_excel)
                break
            except Exception as e:
                log("error", f"Error en intento {intento} para {nombre}: {e}")
                if intento == MAXIMOS_REINTENTOS_POR_PACIENTE:
                    log("error", f"{EMOJI_STOP} Fallaron todos los intentos para {nombre}. Omitiendo paciente.")
                    result_paciente = {
                        "Fecha": fecha_excel,
                        "Rut": rut,
                        "Nombre": nombre,
                        "Año Creación Caso": "N/A",
                        "Antigüedad Caso": "Sin fecha",
                        "Apto para 3114103": "No",
                        "Información Adicional": "Fallo crítico en procesamiento"
                    }
            time.sleep(3)

        if result_paciente:
            resultados.append(result_paciente)

        # Volver a inicio (best effort)
        btn_ini = esperar_elemento(driver, XPATH_BTN_INICIO)
        if btn_ini:
            try:
                btn_ini.click()
                esperar_a_que_cargue(driver)
            except Exception:
                pass

    if resultados:
        os.makedirs(RUTA_CARPETA_SALIDA, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        out_path = os.path.join(RUTA_CARPETA_SALIDA, f"Revision_{NOMBRE_DE_LA_MISION}_{timestamp}.xlsx")
        df_out = pd.DataFrame(resultados)

        columnas_base = ["Fecha", "Rut", "Nombre"]
        columnas_misiones = []
        for m in SECUENCIA_DE_MISIONES:
            codigo = m["codigo_requerido"]
            columnas_misiones.extend([
                f"Misión {codigo}", f"Encontrada {codigo}", f"Misma Fecha {codigo}"
            ])

        columnas_finales = columnas_base + columnas_misiones + [
            "Año Creación Caso", "Antigüedad Caso", "Apto para 3114103", "Información Adicional"
        ]
        columnas_existentes = [c for c in columnas_finales if c in df_out.columns]
        df_out = df_out[columnas_existentes]
        df_out.to_excel(out_path, index=False)
        log("exito", f"✅ Revisión completada. Archivo generado: {out_path}")
    else:
        log("warn", "No se generaron resultados. No se creó archivo de salida.")

if __name__ == "__main__":
    ejecutar_revision()
