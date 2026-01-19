# -*- coding: utf-8 -*-
import os
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from colorama import Fore, Style, Back, init
import unicodedata

# =================================================================================
# 🎮 PANEL DE CONTROL OMEGA – CGO: Cardiopatías Congénitas Operables
# =================================================================================

NOMBRE_DE_LA_MISION = "Cardiopatías Congénitas Operables"

# Excel de entrada (ajusta ruta si corresponde)
RUTA_ARCHIVO_ENTRADA = r"C:\Users\Usuario HGF\Desktop\\Trabajo\Cardiologia.xlsx"  # <-- CAMBIA si usas otro

# Carpeta de salida
RUTA_CARPETA_SALIDA = r"C:\Users\Usuario HGF\Desktop\Trabajo\Extra\Revisiones"

# Misiones:
# - "lista_codigos": cualquiera de estos códigos habilita
# - "codigo": seguimiento 3111003 (evitar duplicar en la misma fecha Excel)
SECUENCIA_DE_MISIONES = [
    {
        "nombre_mision": "Proc Habilitantes CGO",
        "etiqueta_columnas": "PROC-Habilitantes",
        # Usa términos robustos (sin tildes/minúsculas) para reconocer el caso
        "keywords_caso": ["cardiopatías", "cardiopatías congenitas", "cardiopatias congenitas", "congenitas operables", "congénitas operables"],
        "tipo_busqueda": "lista_codigos",
        "codigos_requeridos": [
            "1701141","1701142","1703047","1703049","1703050","1703051",
            "1703054","1703055","1703061","1703062","1703063",
            "1703148","1703153","1703163","1703253","2501124"
        ],
        "detener_al_exito": False
    },
    {
        "nombre_mision": "Seguimiento CGO",
        "etiqueta_columnas": "3111003",
        "keywords_caso": ["cardiopatías", "cardiopatías congenitas", "cardiopatias congenitas", "congenitas operables", "congénitas operables"],
        "tipo_busqueda": "codigo",
        "codigo_requerido": "3111003",
        "detener_al_exito": True
    },
]

# Columnas en el Excel de entrada (0-based)
INDICE_COLUMNA_FECHA = 0
INDICE_COLUMNA_RUT = 2
INDICE_COLUMNA_NOMBRE = 4

# WebDriver Edge (debug)
DIRECCION_DEBUG_EDGE = "localhost:9222"
EDGE_DRIVER_PATH = r"C:\\Windows\\System32\\msedgedriver.exe"

# Reintentos por paciente
MAXIMOS_REINTENTOS_POR_PACIENTE = 3

# ============================ FIN DEL PANEL DE CONTROL ==============================

# ====== LOGGING / COLORES ======
init(autoreset=True)
EMOJI_OK, EMOJI_NO, EMOJI_WARN = "✅", "❌", "⚠️"
EMOJI_START, EMOJI_CASE, EMOJI_CODE, EMOJI_SPINNER = "🚀", "📋", "💉", "🌀"
EMOJI_STOP, EMOJI_ROBOT, EMOJI_SKULL = "🛑", "🤖", "💀"

def _c(s): return Fore.CYAN + s + Style.RESET_ALL
def _g(s): return Fore.GREEN + s + Style.RESET_ALL
def _y(s): return Fore.YELLOW + s + Style.RESET_ALL
def _r(s): return Fore.RED + s + Style.RESET_ALL
def _w(s): return Fore.WHITE + s + Style.RESET_ALL
def _bold(s): return Style.BRIGHT + s + Style.NORMAL

def banner_paciente(nombre, rut, fecha_excel, i=None, total=None):
    head = f"{EMOJI_CASE}  {_bold('Paciente:')} {_w(nombre)}  |  {_bold('RUT:')} {_w(rut)}  |  {_bold('Fecha Objetivo:')} {_w(fecha_excel)}"
    if i is not None and total is not None:
        head = f"{_w(f'[{i}/{total}]')}  " + head
    print(Back.BLUE + " " * 3 + Style.RESET_ALL + " " + head)

def log(tipo: str, mensaje: str) -> None:
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

def log_mision_resumen(etiqueta, estado, fecha_encontrada, misma_fecha, codigo="N/A"):
    estado_fmt = _g(estado) if estado.lower() != "sin caso" else _y(estado)
    if fecha_encontrada == "N/A":
        detalle = _y("No se encontró prestación")
    else:
        if misma_fecha in ("Sí", "No"):
            coincide = _g("Sí") if misma_fecha == "Sí" else _r("No")
            detalle = f"Código: {_w(codigo)} | Encontrada: {_w(fecha_encontrada)} | Misma Fecha: {coincide}"
        else:
            detalle = f"Código: {_w(codigo)} | Encontrada: {_w(fecha_encontrada)}"
    print(f"   {_w('[' + etiqueta + ']')} {estado_fmt}  |  {detalle}")

def log_encontrado_por(tipo, objetivo, fecha, coincide, extra=""):
    base = f"{tipo} {_w(str(objetivo))} encontrado el {_w(fecha)}"
    if coincide == "Sí":
        print(_g(f"{EMOJI_OK} {base} (coincide con Excel){extra}"))
    elif coincide == "No":
        print(_y(f"{EMOJI_WARN} {base} (no coincide con Excel){extra}"))
    else:
        print(_c(f"{EMOJI_CODE} {base}{extra}"))

# ====== SELECTORES / COLUMNAS DE LA WEB ======
CSS_SELECTOR_SPINNER = "dialog.loading"

ESTADOS_ACTIVOS = [
    "caso confirmado", "caso activo", "caso en tratamiento",
    "caso en sospecha", "caso en seguimiento", "caso con estudio de pre-transplante",
    "caso en proceso de diagnóstico", "tratamiento", "Caso Confirmado Otras Card. Congénitas Operables"
]

# XPaths (ajusta si cambian en el DOM)
XPATH_RUT = "/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/div/div/input"
XPATH_BTN_BUSCAR = "/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/button/p"
XPATH_CARTOLA = "/html/body/div/main/div[2]/nav/div[1]/div[2]/a[4]/p"
XPATH_CHECKBOX_HITOS = "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div/div/label/input"
XPATH_LISTA_CASOS_ROOT = "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]"
XPATH_BTN_INICIO = "/html/body/div/main/div[2]/nav/div[1]/div[2]/a[1]/p"

# Índices de columnas en la tabla de prestaciones (0-based)
COL_FECHA_DIGITACION = 2
COL_CODIGO_PRESTACION = 7
COL_DESCRIPCION_PRESTACION = 8

def get_xpath_caso_n(idx: int) -> str:
    return f"{XPATH_LISTA_CASOS_ROOT}/div[{idx}]"

def get_xpath_checkbox_caso_n(idx: int) -> str:
    return f"{get_xpath_caso_n(idx)}/div/label/input"

def get_xpath_tabla_prestaciones_caso_n(idx: int) -> str:
    return f"{get_xpath_caso_n(idx)}/div[6]/div[2]/div/table"

def get_xpath_tbody_prestaciones_caso_n(idx: int) -> str:
    return f"{get_xpath_tabla_prestaciones_caso_n(idx)}/tbody"

# ====== UTILIDADES ======
def esperar_a_que_cargue(driver: webdriver.Edge, timeout: int = 30) -> bool:
    try:
        WebDriverWait(driver, timeout).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, CSS_SELECTOR_SPINNER)))
        time.sleep(1)
        return True
    except TimeoutException:
        log("error", f"El sistema se quedó pegado esperando la carga {EMOJI_SPINNER}.")
        return False

def esperar_elemento(driver: webdriver.Edge, xpath: str, timeout: int = 15):
    try:
        return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    except TimeoutException:
        log("warn", f"No se encontró el elemento esperado: {xpath}")
        return None

def solo_fecha(dt) -> str:
    if isinstance(dt, datetime):
        return dt.strftime("%d/%m/%Y")
    s = str(dt).split(' ')[0].replace('-', '/')
    parts = s.split('/')
    if len(parts) >= 3 and len(parts[0]) == 4:
        return f"{parts[2]}/{parts[1]}/{parts[0]}"
    return s

def _normalize_text(s: str) -> str:
    s = s or ""
    s = s.lower()
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

# ====== NÚCLEO DE REVISIÓN ======
def revisar_prestaciones(driver: webdriver.Edge, idx_caso: int, mision: dict, fecha_excel: str):
    """
    Busca dentro de la tabla de prestaciones del caso desplegado según la misión:
    - Por código exacto
    - Por lista de códigos (retorna el más reciente)
    - Por texto en descripción (contains, sin tildes)
    Devuelve: { "codigo_encontrado", "fecha_digitacion", "misma_fecha" }
    """
    resultado = {
        "codigo_encontrado": None,
        "fecha_digitacion": "N/A",
        "misma_fecha": "N/A"
    }

    try:
        tbody = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, get_xpath_tbody_prestaciones_caso_n(idx_caso)))
        )
        filas = tbody.find_elements(By.TAG_NAME, "tr")

        tipo = mision.get("tipo_busqueda", "codigo")
        objetivo_codigo = (mision.get("codigo_requerido") or "").strip()
        objetivo_lista = [c.strip() for c in (mision.get("codigos_requeridos") or [])]
        objetivo_texto = _normalize_text(mision.get("texto_requerido") or "")

        # Recorremos de más reciente a más antiguo
        for fila in reversed(filas):
            cols = fila.find_elements(By.TAG_NAME, "td")
            if len(cols) <= max(COL_CODIGO_PRESTACION, COL_DESCRIPCION_PRESTACION, COL_FECHA_DIGITACION):
                continue

            fecha_completa = cols[COL_FECHA_DIGITACION].text.strip()
            fecha_sola = fecha_completa.split(' ')[0]
            codigo_actual = cols[COL_CODIGO_PRESTACION].text.strip()

            if tipo == "codigo" and objetivo_codigo:
                if codigo_actual == objetivo_codigo:
                    resultado["codigo_encontrado"] = codigo_actual
                    resultado["fecha_digitacion"] = fecha_sola
                    resultado["misma_fecha"] = "Sí" if fecha_sola == fecha_excel else "No"
                    log_encontrado_por("Código", objetivo_codigo, fecha_sola, resultado["misma_fecha"])
                    return resultado

            elif tipo == "lista_codigos" and objetivo_lista:
                if codigo_actual in objetivo_lista:
                    resultado["codigo_encontrado"] = codigo_actual
                    resultado["fecha_digitacion"] = fecha_sola
                    resultado["misma_fecha"] = "N/A"
                    log_encontrado_por("Código (habilitante)", codigo_actual, fecha_sola, "N/A")
                    return resultado

            elif tipo == "texto" and objetivo_texto:
                desc_actual = _normalize_text(cols[COL_DESCRIPCION_PRESTACION].text.strip())
                if objetivo_texto in desc_actual:
                    resultado["codigo_encontrado"] = codigo_actual or "N/A"
                    resultado["fecha_digitacion"] = fecha_sola
                    resultado["misma_fecha"] = "Sí" if fecha_sola == fecha_excel else "No"
                    log_encontrado_por("Texto", mision.get('texto_requerido'), fecha_sola, resultado["misma_fecha"],
                                       extra=_w(f"  (código fila: {codigo_actual})"))
                    return resultado

    except Exception as e:
        log("error", f"Error al revisar prestaciones: {e} 🐛")

    return resultado

def analizar_paciente(driver: webdriver.Edge, nombre: str, rut: str, fecha_excel: str):
    resultado = {
        "Fecha": fecha_excel,
        "Rut": rut,
        "Nombre": nombre,
        "Información Adicional": ""
    }

    # Inicializamos columnas por misión según su etiqueta única
    for mision in SECUENCIA_DE_MISIONES:
        etiqueta = mision['etiqueta_columnas']
        resultado[f"Misión [{etiqueta}]"] = "Sin caso"
        resultado[f"Código [{etiqueta}]"] = "N/A"        # NUEVO: guardamos el código detectado
        resultado[f"Encontrada [{etiqueta}]"] = "N/A"
        resultado[f"Misma Fecha [{etiqueta}]"] = "N/A"

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
            chk_hitos.click()
            esperar_a_que_cargue(driver)

        lista_casos = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, XPATH_LISTA_CASOS_ROOT))
        )
        casos_divs = lista_casos.find_elements(By.CSS_SELECTOR, "div.contRow")

        # Normalizamos texto de casos (minúsculas + sin tildes)
        casos_texto = [_normalize_text(c.text) for c in casos_divs]

        # Flags para "Información Adicional" (si quieres algo extra en el futuro)
        # Aquí no las usamos, pero puedes extender.
        # keywords globales (normalizadas)
        kw_global = ["cardiopatias", "congenitas", "operables"]

        # Recorremos misiones
        for mision in SECUENCIA_DE_MISIONES:
            etiqueta = mision['etiqueta_columnas']
            idx_target = None
            estado_detectado = None

            kw_local = mision.get('keywords_caso', kw_global)
            kw_local = [_normalize_text(k) for k in kw_local]

            # Elegimos el caso que cumpla keywords + estado activo
            for i, texto_caso in enumerate(casos_texto):
                is_active = any(est in texto_caso for est in ESTADOS_ACTIVOS)
                if not is_active:
                    continue
                if all(kw in texto_caso for kw in kw_local):
                    idx_target = i + 1
                    estado_detectado = next((est for est in ESTADOS_ACTIVOS if est in texto_caso), None)
                    if estado_detectado:
                        resultado[f"Misión [{etiqueta}]"] = estado_detectado.title()
                    break

            if idx_target:
                chk_xpath = get_xpath_checkbox_caso_n(idx_target)
                chk = esperar_elemento(driver, chk_xpath)
                if chk:
                    driver.execute_script("arguments[0].scrollIntoView(true);", chk)
                    chk.click()
                    esperar_a_que_cargue(driver)

                    verif = revisar_prestaciones(driver, idx_target, mision, fecha_excel)
                    resultado[f"Código [{etiqueta}]"] = verif.get('codigo_encontrado') or "N/A"
                    resultado[f"Encontrada [{etiqueta}]"] = verif['fecha_digitacion']
                    resultado[f"Misma Fecha [{etiqueta}]"] = verif['misma_fecha']

                    # Resumen de la misión (bonito)
                    estado_actual = resultado.get(f"Misión [{etiqueta}]", "Sin caso")
                    log_mision_resumen(
                        etiqueta=etiqueta,
                        estado=estado_actual,
                        fecha_encontrada=verif['fecha_digitacion'],
                        misma_fecha=verif['misma_fecha'],
                        codigo=verif.get('codigo_encontrado') or "N/A"
                    )

                    # Cerramos el acordeón del caso si se puede
                    try:
                        chk2 = esperar_elemento(driver, chk_xpath)
                        if chk2:
                            chk2.click()
                            esperar_a_que_cargue(driver)
                    except Exception:
                        pass

                    if mision['detener_al_exito']:
                        break
            else:
                # No se encontró un caso que matchee los keywords/estado activo
                log_mision_resumen(
                    etiqueta=etiqueta,
                    estado="Sin caso",
                    fecha_encontrada="N/A",
                    misma_fecha="N/A",
                    codigo="N/A"
                )

        # ---- Cálculo de "Apto para 3111003"
        cod_habil = resultado.get("Código [PROC-Habilitantes]", "N/A")
        fecha_311 = resultado.get("Encontrada [3111003]", "N/A")
        misma_311 = resultado.get("Misma Fecha [3111003]", "N/A")

        tiene_habil = cod_habil not in (None, "", "N/A")
        dup_311_mismo_dia = (fecha_311 not in (None, "", "N/A")) and (misma_311 == "Sí")

        resultado["Apto para 3111003"] = "Sí" if (tiene_habil and not dup_311_mismo_dia) else "No"

        # Info adicional bonita
        if tiene_habil:
            info = f"Habilitante más reciente: {cod_habil} el {resultado.get('Encontrada [PROC-Habilitantes]', 'N/A')}"
            resultado["Información Adicional"] = (resultado.get("Información Adicional","") + " | " + info).strip(" |")

    except Exception as e:
        log("error", f"Error general al revisar al paciente {nombre}: {e}")

    return resultado

# ====== PIPELINE PRINCIPAL ======
def ejecutar_revision():
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
        total = len(df)
        log("info", f"Archivo cargado: {RUTA_ARCHIVO_ENTRADA} con {total} pacientes.")
    except Exception as e:
        log("error", f"No se pudo leer el archivo Excel: {e}")
        return

    # Contadores para resumen final por misión
    resumen_misiones = {m["etiqueta_columnas"]: 0 for m in SECUENCIA_DE_MISIONES}

    resultados = []
    for index, row in df.iterrows():
        nombre = str(row.iloc[INDICE_COLUMNA_NOMBRE]).strip()
        rut = str(row.iloc[INDICE_COLUMNA_RUT]).strip()
        fecha_excel = solo_fecha(row.iloc[INDICE_COLUMNA_FECHA])

        result_paciente = None
        for intento in range(1, MAXIMOS_REINTENTOS_POR_PACIENTE + 1):
            try:
                if intento == 1:
                    banner_paciente(nombre, rut, fecha_excel, i=index+1, total=len(df))
                log("info", f"Intento {intento} {_w('(conectando y revisando...)')}")
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
                        "Apto para 3111003": "No",
                        "Información Adicional": "Fallo crítico en procesamiento"
                    }
            time.sleep(2.0)

        if result_paciente:
            # sumar hits por misión (si tiene fecha encontrada != N/A)
            for m in SECUENCIA_DE_MISIONES:
                etq = m["etiqueta_columnas"]
                if result_paciente.get(f"Encontrada [{etq}]") not in (None, "N/A", ""):
                    resumen_misiones[etq] += 1

            resultados.append(result_paciente)

        # Volver a inicio
        btn_ini = esperar_elemento(driver, XPATH_BTN_INICIO)
        if btn_ini:
            try:
                btn_ini.click()
                esperar_a_que_cargue(driver)
            except Exception:
                pass

    # Exportar Excel
    if resultados:
        os.makedirs(RUTA_CARPETA_SALIDA, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        out_path = os.path.join(RUTA_CARPETA_SALIDA, f"Revision_{NOMBRE_DE_LA_MISION}_{timestamp}.xlsx")
        df_out = pd.DataFrame(resultados)

        columnas_base = ["Fecha", "Rut", "Nombre"]
        columnas_misiones = []
        for m in SECUENCIA_DE_MISIONES:
            etiqueta = m["etiqueta_columnas"]
            columnas_misiones.extend([
                f"Misión [{etiqueta}]",
                f"Código [{etiqueta}]",        # incluye el código encontrado (habilitante o 3111003)
                f"Encontrada [{etiqueta}]",
                f"Misma Fecha [{etiqueta}]"
            ])

        columnas_finales = columnas_base + columnas_misiones + ["Apto para 3111003", "Información Adicional"]
        columnas_existentes = [c for c in columnas_finales if c in df_out.columns]
        df_out = df_out[columnas_existentes]
        df_out.to_excel(out_path, index=False)
        log("exito", f"✅ Revisión completada. Archivo generado: {out_path}")

        # Resumen final por misión
        log("info", _bold("Resumen final (coincidencias por misión):"))
        for m in SECUENCIA_DE_MISIONES:
            etq = m["etiqueta_columnas"]
            log("info", f"   {_w(etq)} → {_g(str(resumen_misiones[etq]))} hallazgos")

    else:
        log("warn", "No se generaron resultados. No se creó archivo de salida.")

# ====== ENTRYPOINT ======
if __name__ == "__main__":
    ejecutar_revision()
