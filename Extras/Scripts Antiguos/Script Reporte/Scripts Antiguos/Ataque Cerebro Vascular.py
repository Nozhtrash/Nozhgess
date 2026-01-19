import os
import time
import pandas as pd
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, WebDriverException, StaleElementReferenceException,
    ElementClickInterceptedException, JavascriptException,
    ElementNotInteractableException
)
from selenium.webdriver.common.action_chains import ActionChains

from colorama import Fore, Style, init

################################################################################
# PANEL DE CONTROL (Modifica las siguientes variables según tu necesidad)      #
################################################################################

# Nombre de la misión y rutas de archivos
# Para Reporte, este nombre aparecerá en el nombre del archivo de salida.
NOMBRE_DE_LA_MISION = "Reporte"  # Por defecto "reporte"; modifícalo si deseas un nombre diferente

# Ruta del archivo Excel de entrada
# Aquí se almacena el reporte con las distintas hojas de patologías.
RUTA_ARCHIVO_ENTRADA = r"C:\Users\Usuario HGF\Desktop\Trabajo\Reporte Farmacia 11-17 Agosto.xlsx"

# Nombre de la hoja que se desea procesar dentro del Excel. Cada hoja puede
# representar una patología distinta. Cambie HOJA para seleccionar la hoja.
HOJA = "ACV"  # Cambiar al nombre de la hoja que corresponda a la patología

# Carpeta en la que se guardarán los archivos de salida. Se creará si no existe.
RUTA_CARPETA_SALIDA = r"C:\\Users\\Usuario HGF\\Desktop\\Trabajo\\Extra\\Revisiones"

# Conexión al WebDriver Edge en modo debug. Asegúrese de que Microsoft Edge
# esté ejecutándose con el puerto de depuración habilitado (por ejemplo,
# ejecutando `msedge.exe --remote-debugging-port=9222`).
DIRECCION_DEBUG_EDGE = "localhost:9222"
EDGE_DRIVER_PATH = r"C:\\Windows\\System32\\msedgedriver.exe"

# Reintentos y tiempos de espera
MAXIMOS_REINTENTOS_POR_PACIENTE = 3  # Número de veces que se intenta un paciente ante errores
ESPERA_ENTRE_INTENTOS_SEG = 3        # Segundos de espera entre reintentos

# Índices de columnas dentro del Excel de entrada (base 0)
# Para Reporte: RUT en columna B (1), Nombre en D (3) y Fecha en F (5).
INDICE_COLUMNA_FECHA = 5
INDICE_COLUMNA_RUT   = 1
INDICE_COLUMNA_NOMBRE= 3

# Fecha de los códigos habilitantes se considera válida si es ≤ a la fecha objetivo
HABIL_INCLUSIVO_MISMO_DIA = True

# Misiones a ejecutar. Cada misión representa una patología con sus
# correspondientes palabras clave para identificar el caso, un código
# principal (prestación) a buscar y una lista de códigos habilitantes
# opcionales. Si hay más de un código principal, añada una segunda misión
# en la lista. Ejemplo de estructura:
# {
#     "nombre": "Nombre de la patología",
#     "keywords_caso": ["palabra1", "palabra2"],
#     "codigo_principal": "1234567",
#     "habilitantes": {
#         "enabled": True,
#         "require_any": True,
#         "codes": ["7654321", "7654322"]
#     },
#     "mensual": True  # indicar si se desea evaluar periodicidad mensual
# }
MISSIONS: List[Dict[str, Any]] = [
    {
        "nombre": "Accidente Cerebrovascular",
        "keywords_caso": ["ataque cerebrovascular", "ataque"],
        "codigo_principal": "2508017",
        "habilitantes": {
            "enabled": False,
            "require_any": True,
            "codes": ["2508017"]
        },
        "mensual": False
    }
]

# Flag de depuración: si es True, la consola mostrará las prestaciones
# encontradas (códigos y fechas) después de analizar cada caso. Esto
# puede ayudar a diagnosticar por qué un código no aparece en el
# reporte o si la lectura está incompleta. Mantener en False para
# evitar demasiada salida en producción.
DEBUG_PRINT_CODES = False

################################################################################
# LOGGING Y EMOJIS                                                            #
################################################################################

init(autoreset=True)
EMOJI_OK, EMOJI_NO, EMOJI_WARN = "✅", "❌", "⚠️"
EMOJI_STOP, EMOJI_ROBOT = "🛑", "🤖"

def log(tipo: str, mensaje: str) -> None:
    """Imprime mensajes de log con colores y emojis según el tipo.

    `tipo` puede ser uno de: 'exito', 'error', 'info', 'warn', 'debug'.
    Para mantener la consola legible, evita imprimir mensajes muy
    frecuentes dentro de bucles internos; utiliza los niveles
    adecuados para dar contexto de alto nivel.
    """
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
        "debug": EMOJI_STOP
    }
    print(f"{colores.get(tipo, Fore.WHITE)}{emojis.get(tipo, '')} {mensaje}{Style.RESET_ALL}")

def _badge(texto: str, color: str = Fore.WHITE) -> str:
    """Devuelve un texto encerrado entre corchetes con color, para títulos."""
    return f"{color}[{texto}]{Style.RESET_ALL}"

def _kv(k: str, v: str, k_color: str = Fore.WHITE, v_color: str = Fore.CYAN) -> str:
    """Construye una pareja clave:valor coloreada."""
    return f"{k_color}{k}:{Style.RESET_ALL} {v_color}{v}{Style.RESET_ALL}"

def _estado_color(estado: str) -> Tuple[str, str]:
    """Asigna un color e icono según el texto de estado de un caso."""
    s = (estado or "").lower()
    if "cerrado" in s:
        return Fore.RED, "🔒"
    if "sin caso" in s:
        return Fore.WHITE, "—"
    # Usar la lista de términos definidos para colorear en verde
    if any(x in s for x in ESTADOS_COLOREAR_VERDE):
        return Fore.GREEN, "🟢"
    return Fore.YELLOW, "🟨"

################################################################################
# SELECTORES PRINCIPALES (XPATHS A LO TRAUMA)                                 #
################################################################################

# CSS selector del spinner de carga. Se espera a que desaparezca para continuar.
CSS_SELECTOR_SPINNER = "dialog.loading"

# Lista de términos usados únicamente para colorear el estado en la consola.
# No se utiliza para filtrar los casos que se revisan. Esta lista se emplea
# en la función `_estado_color` para asignar un color verde a estados que
# indiquen atención activa.
ESTADOS_COLOREAR_VERDE = [
    "activo", "tratamiento", "confirmado", "seguimiento", "sospecha",
    "diagnóstico", "diagnostico", "pre-transplante"
]

# XPaths de elementos clave. Se dejan varias alternativas para que
# la búsqueda sea más resiliente a cambios en la UI. El orden importa:
# se intenta desde el más específico al más genérico.

# Campo de entrada del RUT
XPATHS_RUT_INPUT = [
    "/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/div/div/input",
    "//input[@id='rutInput']"
]

# Botón para buscar RUT
XPATHS_BTN_BUSCAR = [
    "/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/button",
    "/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/button/p",
    "//button[@class='botonBase botonStand2']"
]

# Navegación en la barra lateral: búsqueda de paciente
XPATHS_BTN_BUSQUEDA_PACIENTE = [
    "/html/body/div/main/div[2]/nav/div[1]/div[2]/a[1]",
    "/html/body/div/main/div[2]/nav/div[1]/div[2]/a[1]/p",
    "//a[contains(@href,'#/34')]",
    "//p[contains(text(),'Búsqueda de Paciente')]/parent::a"
]

# Cartola Unificada de Paciente
XPATHS_BTN_CARTOLA = [
    "/html/body/div/main/div[2]/nav/div[1]/div[2]/a[4]",
    "/html/body/div/main/div[2]/nav/div[1]/div[2]/a[4]/p",
    "//a[contains(@href,'#/161')]",
    "//p[contains(text(),'Cartola Unificada Paciente')]/parent::a"
]

# Checkbox de Hitos GES (input). Se intentan varias rutas.
XPATHS_CHECKBOX_HITOS_GES = [
    "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div/div/label/input",
    "//p[contains(text(),'Hitos GES')]/ancestor::label/input",
    "//p[contains(text(),'Hitos GES')]/preceding-sibling::input"
]

# Contenedor de la lista de casos dentro de Hitos GES (div que contiene las filas)
XPATHS_LISTA_CASOS_ROOT = [
    "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]",
    "//div[contains(@class,'contRowBox') and contains(@class,'scrollH')]/parent::*"
]

# Estructuras dentro de la tabla de prestaciones
COL_FECHA_DIGITACION = 2  # índice de columna con fecha de digitación (no nos interesa)
COL_FECHA_INICIO     = 3  # índice de columna con fecha de inicio de prestación
COL_CODIGO_PRESTACION= 7  # índice de columna con código de prestación
COL_GLOSA_PRESTACION = 8  # índice de columna con descripción/glosa

################################################################################
# UTILIDADES DE FECHA                                                        #
################################################################################

def solo_fecha(dt: Any) -> str:
    """Convierte cualquier fecha (datetime, string, etc.) a formato dd/mm/yyyy."""
    if isinstance(dt, datetime):
        return dt.strftime("%d/%m/%Y")
    s = str(dt).split(' ')[0].replace('-', '/')
    parts = s.split('/')
    # Si viene como yyyy/mm/dd invertimos
    if len(parts[0]) == 4:
        return f"{parts[2]}/{parts[1]}/{parts[0]}"
    return s

def parse_fecha_ddmmyyyy(s: str) -> Optional[datetime]:
    try:
        return datetime.strptime(s, "%d/%m/%Y")
    except Exception:
        return None

def fecha_valida(f: Optional[datetime], objetivo: Optional[datetime]) -> bool:
    """Devuelve True si `f` es válida con respecto a la fecha objetivo."""
    if not f or not objetivo:
        return False
    return (f <= objetivo) if HABIL_INCLUSIVO_MISMO_DIA else (f < objetivo)

################################################################################
# CLASE DE NAVEGACIÓN Y UTILIDADES SELENIUM                                  #
################################################################################

class SiggesDriver:
    """Encapsula las operaciones sobre el WebDriver para SIGGES.

    Esta clase implementa métodos para esperar el spinner, buscar
    elementos mediante distintos selectores, hacer clic de manera
    segura, navegar entre secciones y leer la información de los
    pacientes. Al centralizar la lógica en una clase es más fácil
    reutilizar y ajustar comportamientos específicos.
    """

    def __init__(self, driver: webdriver.Edge) -> None:
        self.driver = driver

    def esperar_spinner(self,
                        appear_timeout: float = 0.35,
                        disappear_timeout: float = 180,
                        settle: float = 0.2) -> None:
        """Espera condicionalmente a que desaparezca el spinner de carga.

        - Se realiza un sondeo rápido (hasta `appear_timeout` segundos) para
          detectar si el spinner aparece. Si no se detecta, se retorna
          rápidamente tras una pausa de estabilización (`settle`).
        - Si aparece, se espera a que desaparezca hasta `disappear_timeout`
          segundos. Si no desaparece en ese tiempo, se pausa el script
          solicitando intervención manual.
        - Tras desaparecer, se espera `settle` segundos para dejar que
          el DOM se estabilice.
        """
        # Sondar brevemente para verificar aparición del spinner
        try:
            end_appear = time.time() + appear_timeout
            spinner_seen = False
            while time.time() < end_appear:
                if self.driver.find_elements(By.CSS_SELECTOR, CSS_SELECTOR_SPINNER):
                    spinner_seen = True
                    break
                time.sleep(0.05)
        except Exception:
            spinner_seen = False
        if not spinner_seen:
            # No hay spinner visible; pausa mínima para estabilizar
            time.sleep(settle)
            return
        # Esperar a que desaparezca
        try:
            WebDriverWait(self.driver, disappear_timeout).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, CSS_SELECTOR_SPINNER))
            )
        except TimeoutException:
            log("warn", "Spinner no desaparece tras tiempo máximo. Pausando para intervención manual.")
            try:
                input("⚠️ El cargador no se ha detenido. Recarga manual y presiona Enter para continuar…")
            except Exception:
                pass
        # Forzar sincronización y pausa final
        try:
            self.driver.execute_script("return document.readyState")
        except JavascriptException:
            pass
        time.sleep(settle)

    def _find_element(self, selectors: List[str], mode: str = "clickable", timeout: int = 3) -> Optional[Any]:
        """Intenta encontrar un elemento probando una lista de selectores.

        Cada selector debe ser una cadena XPath. Si `mode` es
        "presence" se usa `presence_of_element_located`, si es "visible"
        se usa `visibility_of_element_located` y si es "clickable" se usa
        `element_to_be_clickable`.
        """
        for sel in selectors:
            try:
                by, value = By.XPATH, sel
                if mode == "presence":
                    cond = EC.presence_of_element_located((by, value))
                elif mode == "visible":
                    cond = EC.visibility_of_element_located((by, value))
                else:
                    cond = EC.element_to_be_clickable((by, value))
                return WebDriverWait(self.driver, timeout).until(cond)
            except Exception:
                continue
        return None

    def _safe_click(self,
                    selectors: List[str],
                    scroll: bool = True,
                    retries: int = 2,
                    wait_spinner: bool = False,
                    appear_timeout: float = 0.35,
                    disappear_timeout: float = 25,
                    settle: float = 0.2) -> bool:
        """Realiza clic sobre el primer selector que sea clickable con reintentos.

        Al realizar el clic, opcionalmente espera por un spinner de carga.
        Los reintentos se hacen con timeouts cortos para mejorar la
        reactividad. Si se especifica `wait_spinner=True`, se invoca
        `esperar_spinner` con los parámetros provistos.
        """
        for _ in range(retries):
            element = self._find_element(selectors, mode="clickable", timeout=2)
            if element is None:
                time.sleep(0.2)
                continue
            try:
                if scroll:
                    try:
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block:'center'});", element
                        )
                    except Exception:
                        pass
                try:
                    ActionChains(self.driver).move_to_element(element).pause(0.03).perform()
                except Exception:
                    pass
                element.click()
            except (ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException):
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                except Exception:
                    time.sleep(0.2)
                    continue
            if wait_spinner:
                self.esperar_spinner(appear_timeout=appear_timeout,
                                    disappear_timeout=disappear_timeout,
                                    settle=settle)
            return True
        return False

    def asegurar_en_busqueda(self) -> None:
        """Se asegura de que estamos en la sección de búsqueda de paciente.

        Si el RUTInput no está presente, intenta navegar mediante la
        barra lateral. Como último recurso recarga la URL de búsqueda
        directamente. Esta función no retorna nada; simplemente
        posiciona el navegador en la página correcta.
        """
        try:
            url = self.driver.current_url
            if 'actualizaciones' in url:
                try:
                    self.driver.get("https://www.sigges.cl/#/busqueda-de-paciente")
                    self.esperar_spinner()
                except Exception:
                    pass
        except Exception:
            pass
        campo = self._find_element(XPATHS_RUT_INPUT, mode="presence", timeout=1)
        if campo:
            return
        nav_ok = self._safe_click(XPATHS_BTN_BUSQUEDA_PACIENTE,
                                  scroll=False,
                                  wait_spinner=True,
                                  appear_timeout=0.35,
                                  disappear_timeout=25,
                                  settle=0.2)
        if nav_ok:
            return
        try:
            self.driver.get("https://www.sigges.cl/#/busqueda-de-paciente")
            self.esperar_spinner(appear_timeout=0.35, disappear_timeout=25, settle=0.2)
        except Exception:
            pass

    def ir_a_cartola(self) -> bool:
        """Navega a la Cartola Unificada Paciente desde la barra lateral.

        Devuelve True si se logró hacer clic y se espera el spinner
        correspondiente. Si no se encuentra el elemento devuelve False.
        """
        return self._safe_click(XPATHS_BTN_CARTOLA,
                                scroll=False,
                                wait_spinner=True,
                                appear_timeout=0.35,
                                disappear_timeout=25,
                                settle=0.2)

    def activar_hitos_ges(self) -> None:
        """Activa la visualización de Hitos GES en la cartola.

        Si el checkbox ya está seleccionado no hace nada. Si no se
        encuentra el checkbox se levanta una excepción.
        """
        chk = self._find_element(XPATHS_CHECKBOX_HITOS_GES, mode="presence", timeout=20)
        if not chk:
            raise Exception("No se encontró el checkbox de Hitos GES")
        try:
            ya_on = chk.is_selected()
        except Exception:
            ya_on = False
        if not ya_on:
            self._safe_click(
                XPATHS_CHECKBOX_HITOS_GES,
                scroll=True,
                wait_spinner=True,
                appear_timeout=0.35,
                disappear_timeout=25,
                settle=0.2,
            )
        root = self._find_element(XPATHS_LISTA_CASOS_ROOT, mode="presence", timeout=3)
        if not root:
            log("warn", "Hitos GES activado pero sin contenedor de casos visible")
            return
        end_time = time.time() + 2
        while time.time() < end_time:
            try:
                rows = root.find_elements(By.CSS_SELECTOR, "div.contRow")
                if rows:
                    return
            except StaleElementReferenceException:
                pass
            time.sleep(0.25)
        log("warn", "Hitos GES activado pero no se detectaron filas de casos")

    def lista_de_casos_cartola(self) -> List[str]:
        """Obtiene la lista de descripciones de casos actualmente mostrados.

        Lee directamente el texto de cada `div.contRow`, lo cual incluye
        la enfermedad, la fecha de creación y el estado del caso. Se
        devuelven en minúsculas para facilitar las comparaciones. El
        tiempo de espera para encontrar el contenedor se reduce para
        evitar pausas innecesarias.
        """
        root = self._find_element(XPATHS_LISTA_CASOS_ROOT, mode="presence", timeout=3)
        if not root:
            return []
        descripciones: List[str] = []
        try:
            casos = root.find_elements(By.CSS_SELECTOR, "div.contRow")
            for caso in casos:
                try:
                    text = caso.text.strip().lower()
                    if text:
                        descripciones.append(text)
                except Exception:
                    continue
        except Exception:
            pass
        return descripciones

    def abrir_caso_por_indice(self, idx: int) -> Optional[Any]:
        """Abre un caso de la lista de Hitos GES dado su índice (base 0).

        Devuelve el elemento tbody de la tabla de prestaciones, o None si
        no se pudo obtener.
        """
        numero = idx + 1
        root_base = XPATHS_LISTA_CASOS_ROOT[0]
        xpath_checkbox = f"({root_base})/div[{numero}]/div/label/input"
        xpath_label    = f"({root_base})/div[{numero}]"
        if not self._safe_click([xpath_checkbox, xpath_label], wait_spinner=False):
            return None
        time.sleep(0.3)
        try:
            tbody_xpath = f"({root_base})/div[{numero}]/div[6]/div[2]/div/table/tbody"
            tbody = WebDriverWait(self.driver, 14).until(
                EC.presence_of_element_located((By.XPATH, tbody_xpath))
            )
            return tbody
        except TimeoutException:
            return None

    def cerrar_caso_por_indice(self, idx: int) -> None:
        """Cierra (colapsa) un caso previamente abierto.

        No esperamos spinner al colapsar el caso, ya que este toggle no
        dispara carga completa. Simplemente se hace clic y se da una
        breve pausa para permitir que el panel se repliegue.
        """
        numero = idx + 1
        root_base = XPATHS_LISTA_CASOS_ROOT[0]
        xpath_checkbox = f"({root_base})/div[{numero}]/div/label/input"
        xpath_label    = f"({root_base})/div[{numero}]"
        try:
            self._safe_click([xpath_checkbox, xpath_label], wait_spinner=False)
            time.sleep(0.3)
        except Exception:
            pass

    def leer_prestaciones_desde_tbody(self, tbody: Any) -> List[Dict[str, str]]:
        """Convierte las filas de la tabla de prestaciones a una lista de dicts.

        Cada dict contiene las claves 'fecha' (inicio), 'codigo' y 'glosa'.
        Se ordenan de más recientes a más antiguas (el HTML suele tenerlas
        en orden ascendente, pero invertimos al leer para priorizar las más
        recientes).
        """
        prestaciones: List[Dict[str, str]] = []
        try:
            filas = tbody.find_elements(By.TAG_NAME, "tr")
            for fila in reversed(filas):
                cols = fila.find_elements(By.TAG_NAME, "td")
                if len(cols) > max(COL_FECHA_INICIO, COL_CODIGO_PRESTACION, COL_GLOSA_PRESTACION):
                    fecha_digit = cols[COL_FECHA_DIGITACION].text.strip().split(' ')[0]
                    fecha_inicio = cols[COL_FECHA_INICIO].text.strip().split(' ')[0]
                    codigo       = cols[COL_CODIGO_PRESTACION].text.strip()
                    glosa        = cols[COL_GLOSA_PRESTACION].text.strip()
                    prestaciones.append({
                        "fecha_digitacion": fecha_digit,
                        "fecha": fecha_inicio,
                        "codigo": codigo,
                        "glosa": glosa
                    })
        except Exception as e:
            log("warn", f"No se pudieron leer prestaciones: {e}")
        return prestaciones

    def parse_mini_tabla_busqueda(self) -> List[Tuple[str, str]]:
        """Lee la mini tabla de búsqueda de paciente.

        Después de presionar el botón Buscar RUN, aparece una pequeña
        tabla que resume los casos del paciente. Esta función lee
        cada fila y devuelve una lista de tuplas (nombre_caso,
        estado_caso) en minúsculas. Si no se encuentra la tabla,
        devuelve una lista vacía.
        """
        try:
            table = self.driver.find_element(By.XPATH, "//div[@class='contBody maxW scroll' or contains(@class,'contBody')]/div/div[2]/div/div/table")
        except Exception:
            return []
        results: List[Tuple[str, str]] = []
        try:
            tbody = table.find_element(By.TAG_NAME, "tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 4:
                    nombre_caso = cols[1].text.strip().lower()
                    estado_caso = cols[3].text.strip().lower()
                    results.append((nombre_caso, estado_caso))
        except Exception:
            pass
        return results

    def obtener_fecha_fallecimiento(self) -> Optional[str]:
        """Devuelve la fecha de fallecimiento del paciente actualmente mostrado.

        Extrae la fecha desde la Cartola Unificada (sección de datos del
        paciente) utilizando XPaths conocidos. Si el elemento no existe
        o su texto es "Sin Información", devuelve None.
        """
        xpaths_fallecimiento = [
            "/html/body/div/main/div[3]/div[2]/div[1]/div[1]/div[2]/div[5]/div[2]/div/p",
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[1]/div[2]/div[5]/div[2]/div/p"
        ]
        for xpath in xpaths_fallecimiento:
            try:
                elem = self.driver.find_element(By.XPATH, xpath)
                text = elem.text.strip()
                if text and text.lower() != "sin información":
                    return text
            except Exception:
                continue
        return None

################################################################################
# LÓGICA DE ANÁLISIS POR PACIENTE                                            #
################################################################################

def evaluar_habilitantes_any(prestaciones: List[Dict[str, str]], codigos: List[str], fecha_obj: Optional[datetime]) -> Tuple[bool, Optional[str], Optional[str]]:
    """Busca habilitantes válidos en prestaciones (requiere cualquiera).

    Devuelve una tripla (encontrado, codigo_encontrado, fecha_encontrada).
    Un habilitante es válido si su código está en la lista y su
    fecha de inicio es menor o igual a la fecha objetivo (según
    HABIL_INCLUSIVO_MISMO_DIA). Si hay varios, se retorna el más
    reciente.
    """
    mejor_code: Optional[str] = None
    mejor_fecha: Optional[datetime] = None
    for cod in codigos:
        best: Optional[datetime] = None
        for p in prestaciones:
            if p["codigo"] != cod:
                continue
            f = parse_fecha_ddmmyyyy(p["fecha"])
            if f and fecha_valida(f, fecha_obj) and (best is None or f > best):
                best = f
        if best and (mejor_fecha is None or best > mejor_fecha):
            mejor_fecha, mejor_code = best, cod
    if mejor_code and mejor_fecha:
        return True, mejor_code, mejor_fecha.strftime("%d/%m/%Y")
    return False, None, None

def analizar_paciente(sigges: SiggesDriver, nombre: str, rut: str, fecha_excel_str: str) -> Dict[str, Any]:
    """Analiza un paciente y devuelve un dict con los resultados de cada misión.

    Para cada misión configurada:
      * Identifica si existe un caso que coincida con las palabras clave.
      * Obtiene el estado del caso (activo/cerrado/etc.).
      * Lee las prestaciones para encontrar fechas del código principal y
        habilitantes asociados.
      * Evalúa si el código principal se digitó el mismo día que la
        fecha objetivo.
      * Evalúa habilitantes (si están habilitados en la misión).
      * Evalúa periodicidad mensual (todas las fechas en el mismo mes/año).
    """
    resultado: Dict[str, Any] = {
        "Fecha": fecha_excel_str,
        "Rut": rut,
        "Nombre": nombre
    }
    # Inicializar campos por misión
    for m in MISSIONS:
        cp = m["codigo_principal"]
        resultado[f"Misión {cp}"]      = "Sin caso"
        resultado[f"Encontrada {cp}"]  = "N/A"
        resultado[f"Misma Fecha {cp}"] = "N/A"
        # Habilitantes
        hab = m.get("habilitantes", {})
        if hab.get("enabled"):
            resultado[f"¿Habilitante {cp}?"]       = "No"
            resultado[f"Código Habilitante {cp}"]  = ""
            resultado[f"Fecha Habilitante {cp}"]   = ""
        # Mensual
        resultado[f"Fechas Mensual {cp}"] = ""

    fecha_obj = parse_fecha_ddmmyyyy(fecha_excel_str)

    # 1. Navegar a búsqueda de paciente
    sigges.asegurar_en_busqueda()

    # 2. Ingresar RUT y presionar Buscar
    campo_rut = sigges._find_element(XPATHS_RUT_INPUT, mode="presence", timeout=20)
    if not campo_rut:
        raise Exception("Campo RUT no encontrado")
    try:
        campo_rut.clear()
    except StaleElementReferenceException:
        campo_rut = sigges._find_element(XPATHS_RUT_INPUT, mode="presence", timeout=10)
        campo_rut.clear()
    campo_rut.send_keys(rut)

    if not sigges._safe_click(XPATHS_BTN_BUSCAR):
        raise Exception("Botón Buscar RUN no clickable")
    sigges.esperar_spinner()

    # 3. Utilizar la mini tabla de búsqueda para evaluar presencia de casos.
    mini_cases = sigges.parse_mini_tabla_busqueda()
    sigue_en_revision: Dict[str, bool] = {}
    for m in MISSIONS:
        cp = m["codigo_principal"]
        sigue_en_revision[cp] = True
        if mini_cases:
            hay_match = False
            for nombre_caso, estado_caso in mini_cases:
                if any(kw in nombre_caso for kw in m["keywords_caso"]):
                    hay_match = True
                    break
            if not hay_match:
                resultado[f"Misión {cp}"]      = "Sin caso"
                resultado[f"Encontrada {cp}"]  = "N/A"
                resultado[f"Misma Fecha {cp}"] = "N/A"
                hab = m.get("habilitantes", {})
                if hab.get("enabled"):
                    resultado[f"¿Habilitante {cp}?"]       = "No"
                    resultado[f"Código Habilitante {cp}"]  = ""
                    resultado[f"Fecha Habilitante {cp}"]   = ""
                resultado[f"Fechas Mensual {cp}"] = ""
                sigue_en_revision[cp] = False
    if all(not flag for flag in sigue_en_revision.values()):
        return resultado

    # 4. Entrar a Cartola
    if not sigges.ir_a_cartola():
        raise Exception("No se pudo abrir la Cartola Unificada")
    sigges.esperar_spinner(appear_timeout=0.35, disappear_timeout=25, settle=0.2)

    # Leer fecha de fallecimiento (si existe) del encabezado de la Cartola
    fecha_fallecimiento_str = sigges.obtener_fecha_fallecimiento()
    fecha_fallecimiento = parse_fecha_ddmmyyyy(fecha_fallecimiento_str) if fecha_fallecimiento_str else None

    # Si el paciente falleció antes de la fecha objetivo, no se revisan prestaciones
    if fecha_fallecimiento and fecha_obj and fecha_fallecimiento < fecha_obj:
        for m in MISSIONS:
            cp = m["codigo_principal"]
            resultado[f"Misión {cp}"] = "Fallecido"
            resultado[f"Encontrada {cp}"] = "N/A"
            resultado[f"Misma Fecha {cp}"] = "N/A"
            hab = m.get("habilitantes", {})
            if hab.get("enabled"):
                resultado[f"¿Habilitante {cp}?"]       = "No"
                resultado[f"Código Habilitante {cp}"]  = ""
                resultado[f"Fecha Habilitante {cp}"]   = ""
            resultado[f"Fechas Mensual {cp}"] = ""
        return resultado

    # 5. Activar Hitos GES
    sigges.activar_hitos_ges()

    # 6. Obtener lista de casos en cartola
    casos_desc = sigges.lista_de_casos_cartola()

    # 7. Para cada misión, buscar el primer caso cuyo nombre contenga las keywords
    for m in MISSIONS:
        cp = m["codigo_principal"]
        if not sigue_en_revision.get(cp, True):
            continue
        idx_target: Optional[int] = None
        estado_detectado: Optional[str] = None
        for i, texto in enumerate(casos_desc):
            if any(kw in texto for kw in m["keywords_caso"]):
                idx_target = i
                # Extraer el estado como la última línea del texto o la última parte separada por coma
                estado_detectado = None
                try:
                    lineas = [l.strip() for l in texto.split('\n') if l.strip()]
                    if lineas:
                        estado_detectado = lineas[-1]
                    if not estado_detectado:
                        partes = [p.strip() for p in texto.split(',')]
                        if partes:
                            estado_detectado = partes[-1]
                except Exception:
                    estado_detectado = None
                break
        if idx_target is None:
            continue
        # Guardar estado
        if estado_detectado:
            resultado[f"Misión {cp}"] = estado_detectado.title()
        else:
            resultado[f"Misión {cp}"] = "Con caso"
        # Si caso cerrado y fallecido antes de fecha objetivo, se deja como fallecido
        if estado_detectado and "cerrado" in estado_detectado.lower():
            if fecha_fallecimiento and fecha_obj and fecha_fallecimiento < fecha_obj:
                resultado[f"Misión {cp}"] = "Fallecido"
                resultado[f"Encontrada {cp}"] = "N/A"
                resultado[f"Misma Fecha {cp}"] = "N/A"
                hab = m.get("habilitantes", {})
                if hab.get("enabled"):
                    resultado[f"¿Habilitante {cp}?"]       = "No"
                    resultado[f"Código Habilitante {cp}"]  = ""
                    resultado[f"Fecha Habilitante {cp}"]   = ""
                resultado[f"Fechas Mensual {cp}"] = ""
                sigges.cerrar_caso_por_indice(idx_target)
                continue
        # Abrir el caso y leer prestaciones
        tbody = sigges.abrir_caso_por_indice(idx_target)
        if not tbody:
            log("warn", f"No se pudo abrir el caso {m['nombre']} para leer prestaciones")
            sigges.cerrar_caso_por_indice(idx_target)
            continue
        prestaciones = sigges.leer_prestaciones_desde_tbody(tbody)
        if DEBUG_PRINT_CODES:
            try:
                if prestaciones:
                    cods_str = ", ".join([f"{p['codigo']}@{p['fecha']}" for p in prestaciones])
                    log("debug", f"Prestaciones leídas para '{m['nombre']}' (código {cp}): {cods_str}")
                else:
                    log("debug", f"Sin prestaciones en el caso '{m['nombre']}' (código {cp})")
            except Exception:
                pass
        # Mismo día
        misma = any(p["codigo"] == cp and p["fecha"] == fecha_excel_str for p in prestaciones)
        resultado[f"Misma Fecha {cp}"] = "Sí" if misma else "No"
        # Última fecha del código principal
        ult: Optional[datetime] = None
        for p in prestaciones:
            if p["codigo"] == cp:
                f_dt = parse_fecha_ddmmyyyy(p["fecha"])
                if f_dt and (ult is None or f_dt > ult):
                    ult = f_dt
        if ult:
            resultado[f"Encontrada {cp}"] = ult.strftime("%d/%m/%Y")
        # Habilitantes
        hab = m.get("habilitantes", {})
        if hab.get("enabled") and fecha_obj:
            any_ok, code_hab, date_hab = evaluar_habilitantes_any(prestaciones, hab.get("codes", []), fecha_obj)
            resultado[f"¿Habilitante {cp}?"]       = "Sí" if any_ok else "No"
            resultado[f"Código Habilitante {cp}"]  = code_hab or ""
            resultado[f"Fecha Habilitante {cp}"]   = date_hab or ""
        # Mensual: recoger todas las fechas del código principal en el mismo mes y año
        if m.get("mensual"):
            fechas_mens = []
            dt_obj: Optional[datetime] = parse_fecha_ddmmyyyy(fecha_excel_str)
            if dt_obj:
                for p in prestaciones:
                    if p["codigo"] == cp:
                        f_dt = parse_fecha_ddmmyyyy(p["fecha"])
                        if f_dt and f_dt.year == dt_obj.year and f_dt.month == dt_obj.month:
                            fechas_mens.append(p["fecha"])
            # Eliminar duplicados y ordenar
            if fechas_mens:
                fechas_unicas = sorted(set(fechas_mens), key=lambda d: parse_fecha_ddmmyyyy(d) or datetime.min)
                resultado[f"Fechas Mensual {cp}"] = ", ".join(fechas_unicas)
            else:
                resultado[f"Fechas Mensual {cp}"] = ""
        # Cerrar el caso
        sigges.cerrar_caso_por_indice(idx_target)
    return resultado

################################################################################
# CONSTRUCCIÓN DE COLUMNAS PARA EXCEL                                         #
################################################################################

def construir_columnas_detallado(misiones: List[Dict[str, Any]]) -> List[str]:
    """Construye la lista de columnas para la hoja detallada.

    En Reporte se muestran, para cada misión:
      * M{i} Estado   – estado textual del caso (Activo/Tratamiento/etc.).
      * M{i} Fecha    – fecha de la prestación principal más reciente o N/A.
      * M{i} Mismo D  – Sí/No si el código se digitó el mismo día.
      * M{i} Hab      – Sí/No indicando si se cumple algún habilitante.
      * M{i} Cód Hab  – código habilitante más reciente.
      * M{i} Fecha Hab– fecha habilitante más reciente.
      * M{i} Mensual  – Sí/No si hay alguna prestación en el mismo mes.
    """
    cols = ["Fecha", "Rut", "Nombre"]
    for i, m in enumerate(misiones, start=1):
        cols += [
            f"M{i} Estado",
            f"M{i} Fecha",
            f"M{i} Mismo D"
        ]
        hab = m.get("habilitantes", {})
        if hab.get("enabled"):
            cols += [
                f"M{i} Hab",
                f"M{i} Cód Hab",
                f"M{i} Fecha Hab"
            ]
        cols.append(f"M{i} Mensual")
    return cols

def construir_columnas_resumen(misiones: List[Dict[str, Any]]) -> List[str]:
    """Construye la lista de columnas para la hoja de resumen.

    En el resumen se muestran menos detalles por misión:
      * M{i} Estado     – Válido/Inválido según habilitantes y existencia de caso.
      * M{i} Mismo D    – Sí/No indicando coincidencia exacta de fecha.
      * M{i} Habilitante– Sí/No si se cumple algún habilitante (sólo si habilitantes activados).
      * M{i} Mensual    – Sí/No si hay al menos una prestación en el mismo mes.
    """
    cols = ["Fecha", "Rut", "Nombre"]
    for i, m in enumerate(misiones, start=1):
        cols += [f"M{i} Estado", f"M{i} Mismo D"]
        hab = m.get("habilitantes", {})
        if hab.get("enabled"):
            cols.append(f"M{i} Habilitante")
        cols.append(f"M{i} Mensual")
    return cols

def _valididad_mision(res: Dict[str, Any], m: Dict[str, Any]) -> str:
    cp = m["codigo_principal"]
    hab = m.get("habilitantes", {})
    if not hab.get("enabled"):
        # Si no hay habilitantes, un caso es válido si existe cualquier prestación
        return "Válido" if (res.get(f"Misión {cp}", "Sin caso").lower() != "sin caso") else "Inválido"
    # Con habilitantes, se requiere que exista caso y que el habilitante esté presente
    return "Válido" if res.get(f"¿Habilitante {cp}?", "No") == "Sí" else "Inválido"

def mapear_a_fila_detallado(resultado: Dict[str, Any], misiones: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Mapea un resultado individual a una fila del detallado."""
    fila: Dict[str, Any] = {
        "Fecha": resultado.get("Fecha", ""),
        "Rut":   resultado.get("Rut", ""),
        "Nombre":resultado.get("Nombre", "")
    }
    for i, m in enumerate(misiones, start=1):
        cp = m["codigo_principal"]
        fila[f"M{i} Estado"] = resultado.get(f"Misión {cp}", "Sin caso")
        fila[f"M{i} Fecha"]  = resultado.get(f"Encontrada {cp}", "N/A")
        fila[f"M{i} Mismo D"] = resultado.get(f"Misma Fecha {cp}", "N/A")
        hab = m.get("habilitantes", {})
        if hab.get("enabled"):
            fila[f"M{i} Hab"]      = resultado.get(f"¿Habilitante {cp}?", "No")
            fila[f"M{i} Cód Hab"]  = resultado.get(f"Código Habilitante {cp}", "")
            fila[f"M{i} Fecha Hab"] = resultado.get(f"Fecha Habilitante {cp}", "")
        # Mensual: Sí/No si hay fechas en el mismo mes
        fechas_mensual = resultado.get(f"Fechas Mensual {cp}", "")
        fila[f"M{i} Mensual"] = "Sí" if fechas_mensual else "No"
    return fila

def mapear_a_fila_resumen(resultado: Dict[str, Any], misiones: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Mapea un resultado individual a una fila del resumen."""
    fila: Dict[str, Any] = {
        "Fecha":  resultado.get("Fecha", ""),
        "Rut":    resultado.get("Rut", ""),
        "Nombre": resultado.get("Nombre", "")
    }
    for i, m in enumerate(misiones, start=1):
        cp = m["codigo_principal"]
        fila[f"M{i} Estado"] = _valididad_mision(resultado, m)
        fila[f"M{i} Mismo D"] = resultado.get(f"Misma Fecha {cp}", "N/A")
        hab = m.get("habilitantes", {})
        if hab.get("enabled"):
            fila[f"M{i} Habilitante"] = resultado.get(f"¿Habilitante {cp}?", "No")
        fechas_mensual = resultado.get(f"Fechas Mensual {cp}", "")
        fila[f"M{i} Mensual"] = "Sí" if fechas_mensual else "No"
    return fila

################################################################################
# EJECUCIÓN PRINCIPAL                                                        #
################################################################################

def ejecutar_revision() -> None:
    """Función principal que recorre el Excel de entrada y genera el reporte."""
    log("info", f"Iniciando revisión: {NOMBRE_DE_LA_MISION}")
    # Conectar con el navegador
    try:
        options = webdriver.EdgeOptions()
        options.debugger_address = DIRECCION_DEBUG_EDGE
        driver = webdriver.Edge(service=Service(EDGE_DRIVER_PATH), options=options)
        log("exito", "Conectado a Edge (debug).")
    except WebDriverException as e:
        log("error", f"No se pudo conectar con Edge: {e}")
        return

    sigges = SiggesDriver(driver)

    # Leer Excel de entrada
    try:
        df = pd.read_excel(RUTA_ARCHIVO_ENTRADA, sheet_name=HOJA)
        log("info", f"Entrada: {RUTA_ARCHIVO_ENTRADA} - Hoja '{HOJA}' ({len(df)} pacientes).")
    except Exception as e:
        log("error", f"No se pudo leer el Excel: {e}")
        try:
            driver.quit()
        except Exception:
            pass
        return

    filas_detalle: List[Dict[str, Any]] = []
    filas_resumen: List[Dict[str, Any]] = []
    filas_carga_masiva: List[Dict[str, Any]] = []

    # Recorrer filas (saltamos cabecera si procede, aunque en Reporte se asume que
    # los títulos están en la primera fila). No se elimina la primera fila
    # automáticamente; si desea omitir la cabecera, ajustarlo aquí.
    for _, row in df.iterrows():
        # Obtener datos del Excel
        nombre = str(row.iloc[INDICE_COLUMNA_NOMBRE]).strip()
        rut    = str(row.iloc[INDICE_COLUMNA_RUT]).strip()
        fecha  = solo_fecha(row.iloc[INDICE_COLUMNA_FECHA])
        # Procesar con reintentos
        result: Optional[Dict[str, Any]] = None
        for intento in range(1, MAXIMOS_REINTENTOS_POR_PACIENTE + 1):
            log("info", f"Intento {intento}/{MAXIMOS_REINTENTOS_POR_PACIENTE} para {nombre} ({rut})")
            try:
                result = analizar_paciente(sigges, nombre, rut, fecha)
                break
            except Exception as e:
                log("warn", f"Reintento por error: {e}")
                if intento < MAXIMOS_REINTENTOS_POR_PACIENTE:
                    time.sleep(ESPERA_ENTRE_INTENTOS_SEG)
                    continue
                log("error", f"Fallo crítico en procesamiento de {nombre} (RUT {rut}).")
                try:
                    resp = input("⚠️ Paciente con error. Presiona Enter para reintentar una vez más o '*' para saltar: ").strip()
                except Exception:
                    resp = ''
                if resp == '*':
                    result = {
                        "Fecha": fecha,
                        "Rut": rut,
                        "Nombre": nombre
                    }
                    break
                else:
                    try:
                        result = analizar_paciente(sigges, nombre, rut, fecha)
                    except Exception:
                        result = {
                            "Fecha": fecha,
                            "Rut": rut,
                            "Nombre": nombre
                        }
                    break
        if result is None:
            result = {
                "Fecha": fecha,
                "Rut": rut,
                "Nombre": nombre
            }
        # Imprimir resumen en consola
        imprimir_resumen_paciente(result, MISSIONS)
        # Mapear a filas
        filas_detalle.append(mapear_a_fila_detallado(result, MISSIONS))
        filas_resumen.append(mapear_a_fila_resumen(result, MISSIONS))
        # Construir fila para Carga Masiva (campo fijo sin prestaciones)
        try:
            rut_clean = result.get("Rut", "").strip()
            rut_num, dv = "", ""
            if rut_clean:
                rut_clean2 = rut_clean.replace(".", "").replace(" ", "")
                if "-" in rut_clean2:
                    partes = rut_clean2.split("-")
                    rut_num = partes[0]
                    dv = partes[1]
                else:
                    rut_num = rut_clean2[:-1]
                    dv = rut_clean2[-1]
            fila_carga = {
                "FECHA": result.get("Fecha", ""),
                "RUT": rut_num,
                "DV": dv,
                "PRESTACIONES": "",
                "TIPO": "",
                "PS-FAM": "",
                "ESPECIALIDAD": ""
            }
            filas_carga_masiva.append(fila_carga)
        except Exception:
            filas_carga_masiva.append({
                "FECHA": result.get("Fecha", ""),
                "RUT": result.get("Rut", ""),
                "DV": "",
                "PRESTACIONES": "",
                "TIPO": "",
                "PS-FAM": "",
                "ESPECIALIDAD": ""
            })
        # Asegurar volver a la búsqueda para el siguiente paciente
        try:
            sigges.asegurar_en_busqueda()
        except Exception:
            pass

    # Guardar resultados a Excel
    if filas_detalle:
        try:
            os.makedirs(RUTA_CARPETA_SALIDA, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M")
            out_path = os.path.join(RUTA_CARPETA_SALIDA, f"Revision_{NOMBRE_DE_LA_MISION}_{ts}.xlsx")
            cols_det = construir_columnas_detallado(MISSIONS)
            cols_res = construir_columnas_resumen(MISSIONS)
            df_det = pd.DataFrame(filas_detalle, columns=cols_det)
            df_res = pd.DataFrame(filas_resumen, columns=cols_res)
            cols_carga = ["FECHA", "RUT", "DV", "PRESTACIONES", "TIPO", "PS-FAM", "ESPECIALIDAD"]
            df_carga = pd.DataFrame(filas_carga_masiva, columns=cols_carga)
            with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
                df_res.to_excel(writer, index=False, sheet_name="Resumen")
                df_det.to_excel(writer, index=False, sheet_name="Detallado")
                df_carga.to_excel(writer, index=False, sheet_name="Carga Masiva")
            log("exito", f"Archivo generado: {out_path}")
        except Exception as e:
            log("error", f"Error al generar el Excel de salida: {e}")
    else:
        log("warn", "No se generaron resultados. No se creó archivo de salida.")
    try:
        driver.quit()
    except Exception:
        pass

def imprimir_resumen_paciente(res: Dict[str, Any], misiones: List[Dict[str, Any]]) -> None:
    """Muestra un resumen compacto de los resultados del paciente en consola."""
    print(" ".join([
        _badge("PACIENTE", Fore.MAGENTA),
        _kv("RUT", res.get("Rut", "")), "·",
        _kv("Nombre", res.get("Nombre", ""), v_color=Fore.YELLOW), "·",
        _kv("Fecha Obj", res.get("Fecha", ""), v_color=Fore.WHITE)
    ]))
    for m in misiones:
        cp = m["codigo_principal"]
        estado     = res.get(f"Misión {cp}", "Sin caso")
        encontrada = res.get(f"Encontrada {cp}", "N/A")
        misma      = res.get(f"Misma Fecha {cp}", "N/A")
        col, icon  = _estado_color(estado)
        cod_fecha = f"{cp} | {encontrada}" if encontrada != "N/A" else "—"
        mensual_yes = "Sí" if res.get(f"Fechas Mensual {cp}", "") else "No"
        print(" ".join([
            _badge("CASO", Fore.BLUE), icon,
            _kv("Dx", m["nombre"], v_color=Fore.YELLOW), "·",
            _kv("Código", cp, v_color=Fore.WHITE), "·",
            f"{col}{estado.title()}{Style.RESET_ALL}", "·",
            _kv("Fecha Encontrada", encontrada, v_color=(Fore.GREEN if encontrada != "N/A" else Fore.WHITE)), "·",
            _kv("Misma Fecha", misma, v_color=(Fore.GREEN if misma == "Sí" else (Fore.RED if misma == "No" else Fore.WHITE))), "·",
            _kv("Mensual", mensual_yes, v_color=(Fore.GREEN if mensual_yes == "Sí" else Fore.RED))
        ]))
        hab = m.get("habilitantes", {})
        if hab.get("enabled") and "sin caso" not in (estado or "").lower():
            ok  = res.get(f"¿Habilitante {cp}?", "No") == "Sí"
            cod_h = res.get(f"Código Habilitante {cp}", "")
            fch_h = res.get(f"Fecha Habilitante {cp}", "")
            flag = f"{Fore.GREEN}✓{Style.RESET_ALL}" if ok else f"{Fore.RED}×{Style.RESET_ALL}"
            tail = f"{Fore.WHITE}{cod_h}{Style.RESET_ALL} | {Fore.WHITE}{fch_h}{Style.RESET_ALL}" if ok else "—"
            print(f"   {_badge('HAB', Fore.CYAN)} {flag} {tail}")
    print()

if __name__ == "__main__":
    ejecutar_revision()