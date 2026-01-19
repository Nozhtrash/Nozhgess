# -*- coding: utf-8 -*-
import os, re, time, unicodedata
from datetime import datetime
from typing import List, Optional, Dict, Tuple, Any

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from colorama import Fore, Style, init as colorama_init

# ═════════════════════════════════════════════════════════════════════════════
# PANEL DE CONTROL  (ÚNICO LUGAR CON INSTRUCCIONES)
# - Ajusta rutas, conexión a Edge y columnas del Excel (0-based).
# - Define tus misiones (palabras clave, código objetivo y banderas por misión).
# - Opciones de impresión en consola para controlar el ruido.
# ═════════════════════════════════════════════════════════════════════════════

# ── Rutas y conexión ─────────────────────────────────────────────────────────
NOMBRE_DE_LA_MISION = "ReporteIAM"  # ← nombre para el archivo de salida
RUTA_ARCHIVO_ENTRADA = r"C:\Users\Usuario HGF\Desktop\Trabajo\IAM.xlsx"   # ← ruta Excel

RUTA_CARPETA_SALIDA = r"C:\\Users\\Usuario HGF\\Desktop\\Trabajo\\Extra\\Revisiones"   # ← carpeta salida
DIRECCION_DEBUG_EDGE = "localhost:9222"       # ← puerto de Edge en modo debug
EDGE_DRIVER_PATH = r"C:\\Windows\\System32\\msedgedriver.exe"  # ← ruta al msedgedriver.exe

# ── Excel: posiciones de columnas (0-based) ──────────────────────────────────
INDICE_COLUMNA_FECHA  = 5
INDICE_COLUMNA_RUT    = 1
INDICE_COLUMNA_NOMBRE = 3

# ── Reintentos / timing ──────────────────────────────────────────────────────
MAXIMOS_REINTENTOS_POR_PACIENTE = 2
ESPERA_ENTRE_INTENTOS_SEG = 2
SLEEP_LECTURA_TABLAS = 0.5
VENTANA_VIGENCIA_DIAS = 90   # ventana de vigencia para Habilitantes/NG

# ── Exportación ──────────────────────────────────────────────────────────────
HOJA_POR_MISION = True   # True: una hoja por misión | False: todo junto con prefijos

# ── Opciones de impresión (terminal) ─────────────────────────────────────────
# MINI_TABLA_MODO:
#   "oculto"    → no imprime la mini-tabla
#   "compacto"  → imprime solo filas relevantes (matchean alguna misión)
#   "detallado" → imprime todas las filas (limpias) con ✔ si son relevantes
MINI_TABLA_MODO = "compacto"
OMITIR_EVENTO_SIN_CASO = True  # ignora filas cuyo problema sea “Evento sin caso”
DEBUG_PRINT_CODES = False      # debug: imprime códigos@fechas capturados en la Cartola

# ── Misiones ─────────────────────────────────────────────────────────────────
# Campos por misión:
#   nombre: string (solo para logs)
#   keywords: list[str]  → cómo detectar el caso en la mini-tabla (búsqueda rápida)
#   objetivo: string     → código objetivo (seguimiento) a buscar en la Cartola
#   usar_habilitantes: bool → si False, NO revisa habilitantes NI crea columnas
#   habilitantes: list[str] → lista de códigos habilitantes (se ignoran si usar_habilitantes=False)
#   require_any: bool    → True=solo último habilitante | False=guardar lista
#   top_k: int           → N° de habilitantes a guardar si require_any=False
#   usar_ng: bool        → si False, NO revisa No GES NI crea columnas
TOP_K_HABILITANTES = 1

MISSIONS: List[Dict[str, Any]] = [
    {
        "nombre": "ReporteIAM",
        "keywords": ["infarto agudo"],
        "objetivo": "3007003",
        "usar_habilitantes": True,
        "habilitantes": [
            "3007002",
        ],
        "require_any": True,
        "top_k": 1,
        "usar_ng": True,
    }
]

# ═════════════════════════════════════════════════════════════════════════════
# CONSOLA
# ═════════════════════════════════════════════════════════════════════════════

colorama_init(autoreset=True)
OK, WARN, INFO, ERR, DATA, CODE, RESET = (
    Fore.GREEN+Style.BRIGHT, Fore.YELLOW+Style.BRIGHT, Fore.CYAN+Style.BRIGHT,
    Fore.RED+Style.BRIGHT, Fore.MAGENTA+Style.BRIGHT, Fore.BLUE+Style.BRIGHT, Style.RESET_ALL
)
def log(color: str, msg: str) -> None:
    try: print(color + msg + RESET)
    except: print(msg)

# ═════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════════════════════

_ddmmyyyy = re.compile(r"\b(\d{2}/\d{2}/\d{4})\b")

def _norm(s: str) -> str:
    if not s: return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).replace("\xa0"," ").lower().strip()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]"," ", s))

def has_keyword(texto: str, kws: List[str]) -> bool:
    t = _norm(texto); return any(_norm(k) in t for k in kws)

def solo_fecha(x: Any) -> str:
    if isinstance(x, datetime): return x.strftime("%d/%m/%Y")
    s = str(x).split(" ")[0].replace("-", "/"); p = s.split("/")
    return f"{p[2]}/{p[1]}/{p[0]}" if len(p[0])==4 else s

def dparse(s: str) -> Optional[datetime]:
    try: return datetime.strptime(s.split(" ")[0], "%d/%m/%Y")
    except: return None

def same_month(a: datetime, b: datetime) -> bool: return a.year==b.year and a.month==b.month

def en_vig(fecha_obj: Optional[datetime], dt: Optional[datetime]) -> bool:
    if not (fecha_obj and dt): return False
    d = (fecha_obj-dt).days
    return 0 <= d <= VENTANA_VIGENCIA_DIAS

def listar_habilitantes(prest: List[Dict[str,str]], cods: List[str], fobj: Optional[datetime]) -> List[Tuple[str, datetime]]:
    out = []
    for p in prest:
        c = p.get("codigo","")
        if c in cods:
            f = dparse(p.get("fecha",""))
            if f and (not fobj or f <= fobj): out.append((c,f))
    return sorted(out, key=lambda x:x[1], reverse=True)

# ═════════════════════════════════════════════════════════════════════════════
# NO GES (quimioterapia): solo se calcula si hubo caso GES relevante (abrimos Cartola)
# ═════════════════════════════════════════════════════════════════════════════

XPATHS_CHECKBOX_NO_GES = [
    "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[2]/div[1]/div/label/input",
    "//div[label[contains(normalize-space(.),'Hitos No GES')]]//input[@type='checkbox']",
]
XPATHS_CHECKBOX_NO_GES_SELECT = [
    "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[2]/div[7]/div[1]/div/label/input",
    "//div[label[contains(normalize-space(.),'Prestaciones (Programas Especiales)')]]//input[@type='checkbox']",
]
XPATH_NO_GES_TBODY = "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[2]/div[7]/div[2]/div/table/tbody"
NG_GLOSA_KEYWORDS = ["quimioterapia","quimio"]

def scan_no_ges(driver: Any, fobj: Optional[datetime]) -> Tuple[bool, Optional[str], Optional[datetime]]:
    fechas: List[datetime] = []
    try:
        for xs in (XPATHS_CHECKBOX_NO_GES, XPATHS_CHECKBOX_NO_GES_SELECT):
            for xp in xs:
                try:
                    el = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH,xp)))
                    if not el.is_selected():
                        try: driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                        except: pass
                        try: el.click()
                        except: driver.execute_script("arguments[0].click();", el)
                    break
                except: continue
        tbody = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, XPATH_NO_GES_TBODY)))
        time.sleep(max(0.5, SLEEP_LECTURA_TABLAS))
        for r in tbody.find_elements(By.XPATH,"./tr"):
            try:
                tds = r.find_elements(By.TAG_NAME,"td")
                glosa = (tds[7].text if len(tds)>=8 else "").strip().lower()
                blob = (glosa + " " + (r.text or "") + " " + (r.get_attribute("outerHTML") or "")).lower()
                if not any(k in blob for k in NG_GLOSA_KEYWORDS): continue
                fecha_txt = (tds[1].text or "").strip() if len(tds)>=2 else ""
                fdt = dparse(fecha_txt) or (lambda m: dparse(m.group(1)) if m else None)(_ddmmyyyy.search(blob))
                if not fdt or (fobj and fdt>fobj): continue
                fechas.append(fdt)
            except: continue
    except: pass
    if fechas:
        fmax = max(fechas); return True, fmax.strftime("%d/%m/%Y"), fmax
    return False, None, None

# ═════════════════════════════════════════════════════════════════════════════
# SELENIUM WRAPPER
# ═════════════════════════════════════════════════════════════════════════════

class SiggesDriver:
    def __init__(self, driver: webdriver.Remote) -> None: self.driver = driver

    def esperar_spinner(self, appear_timeout=0.35, disappear_timeout=25, settle=0.2) -> None:
        try:
            end = time.time()+appear_timeout
            seen = False
            while time.time()<end:
                if self.driver.find_elements(By.CSS_SELECTOR,"dialog.loading"): seen=True; break
                time.sleep(0.05)
        except: seen=False
        if not seen: time.sleep(settle); return
        try: WebDriverWait(self.driver, disappear_timeout).until(EC.invisibility_of_element_located((By.CSS_SELECTOR,"dialog.loading")))
        except TimeoutException: pass
        time.sleep(settle)

    def _find(self, xps: List[str], mode="clickable", timeout=3) -> Optional[Any]:
        for xp in xps:
            try:
                cond = {"presence":EC.presence_of_element_located, "visible":EC.visibility_of_element_located}.get(mode, EC.element_to_be_clickable)
                return WebDriverWait(self.driver, timeout).until(cond((By.XPATH,xp)))
            except: continue
        return None

    def _click(self, xps: List[str], scroll=True, wait_spinner=False) -> bool:
        el = self._find(xps,"clickable",2)
        if not el: return False
        try:
            if scroll:
                try: self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                except: pass
            try: ActionChains(self.driver).move_to_element(el).pause(0.02).perform()
            except: pass
            el.click()
        except (ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException):
            try: self.driver.execute_script("arguments[0].click();", el)
            except: return False
        if wait_spinner: self.esperar_spinner()
        return True

    def asegurar_en_busqueda(self) -> None:
        try:
            if "actualizaciones" in self.driver.current_url:
                self.driver.get("https://www.sigges.cl/#/busqueda-de-paciente"); self.esperar_spinner()
        except: pass
        if self._find(["/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/div/div/input"],"presence",1): return
        self._click(["/html/body/div/main/div[2]/nav/div[1]/div[2]/a[1]"], scroll=False, wait_spinner=True)

    def ir_a_cartola(self) -> bool:
        return self._click(["/html/body/div/main/div[2]/nav/div[1]/div[2]/a[4]"], scroll=False, wait_spinner=True)

    def activar_hitos_ges(self) -> None:
        chk = self._find(["/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div/div/label/input"], "presence", 20)
        if not chk: return
        try:
            if not chk.is_selected():
                self._click(["/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div/div/label/input"], True, True)
        except: pass
        root = self._find(["/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]"], "presence", 3)
        end = time.time()+2
        while time.time()<end:
            try:
                if root and root.find_elements(By.CSS_SELECTOR,"div.contRow"): return
            except: pass
            time.sleep(0.25)

    def lista_de_casos_cartola(self) -> List[str]:
        time.sleep(SLEEP_LECTURA_TABLAS)
        root = self._find(["/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]"], "presence", 3)
        if not root: return []
        out=[]
        try:
            for c in root.find_elements(By.CSS_SELECTOR,"div.contRow"):
                try:
                    t = c.text.strip()
                    if t: out.append(t)
                except: continue
        except: pass
        return out

    def abrir_caso_por_indice(self, i:int) -> Optional[Any]:
        n = i+1; base = "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]"
        if not self._click([f"({base})/div[{n}]/div/label/input", f"({base})/div[{n}]"], wait_spinner=False): return None
        time.sleep(0.3)
        try: return WebDriverWait(self.driver,14).until(EC.presence_of_element_located((By.XPATH, f"({base})/div[{n}]/div[6]/div[2]/div/table/tbody")))
        except TimeoutException: return None

    def cerrar_caso_por_indice(self, i:int)->None:
        n=i+1; base="/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]"
        try: self._click([f"({base})/div[{n}]/div/label/input", f"({base})/div[{n}]"], wait_spinner=False); time.sleep(0.3)
        except: pass

    def leer_prestaciones_desde_tbody(self, tbody: Any) -> List[Dict[str,str]]:
        out=[]
        try:
            for tr in reversed(tbody.find_elements(By.TAG_NAME,"tr")):
                tds = tr.find_elements(By.TAG_NAME,"td")
                if len(tds)>8:
                    f = (tds[2].text.strip().split(" ")[0] if len(tds)>2 else "")
                    if not dparse(f):
                        for c in tds:
                            m=_ddmmyyyy.search(c.text)
                            if m: f = m.group(1); break
                    out.append({"fecha":f,"codigo":tds[7].text.strip(),"glosa":tds[8].text.strip()})
        except: pass
        return out

    def leer_fallecimiento(self) -> Optional[datetime]:
        try:
            for el in self.driver.find_elements(By.XPATH, "//div[span[normalize-space(.)='Fecha de fallecimiento'] and p]"):
                try:
                    f = dparse(el.find_element(By.TAG_NAME,"p").text.strip())
                    if f: return f
                except: continue
        except: pass
        return None

# ═════════════════════════════════════════════════════════════════════════════
# MINI TABLA (búsqueda rápida)
# ═════════════════════════════════════════════════════════════════════════════

XPATH_MINI_TBODY_CANDIDATES = [
    "/html/body/div/main/div[3]/div[3]/div/div[2]/div/div/table/tbody",
    "//div[@class='contBody maxW scroll']//div[contains(@class,'cardTable')]/table/tbody",
]

def leer_mini_tabla_busqueda(driver: Any) -> List[Dict[str,str]]:
    tbody=None
    for xp in XPATH_MINI_TBODY_CANDIDATES:
        try: tbody = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH,xp))); break
        except: continue
    if not tbody: return []
    time.sleep(SLEEP_LECTURA_TABLAS)
    out=[]
    for tr in tbody.find_elements(By.XPATH,"./tr"):
        try:
            tds=tr.find_elements(By.TAG_NAME,"td")
            if len(tds)>=4:
                prob, dec, est = tds[1].text.strip(), tds[2].text.strip(), tds[3].text.strip()
                if prob: out.append({"problema":prob,"decreto":dec,"estado":est})
        except: continue
    # Filtro: eliminar "Evento sin caso"
    if OMITIR_EVENTO_SIN_CASO:
        out = [r for r in out if "evento sin caso" not in _norm(r["problema"])]
    return out

# ═════════════════════════════════════════════════════════════════════════════
# LÓGICA DE MISIONES
# ═════════════════════════════════════════════════════════════════════════════

def elegir_caso_mas_reciente(casos: List[str], kws: List[str]) -> Tuple[Optional[int], Optional[str], Optional[datetime]]:
    best=(None,None,None)
    for i, t in enumerate(casos):
        if not has_keyword(t, kws): continue
        m=_ddmmyyyy.search(t); f = dparse(m.group(1)) if m else datetime.min
        if best[2] is None or f>best[2]: best=(i, t.strip(), f)
    return best

def mensual_categoria(fechas: List[datetime], fobj: datetime) -> str:
    if not fechas: return "Sin Día"
    u=sorted(set(fechas)); md = any(f==fobj for f in u)
    pri=[f for f in u if f.day<=15]; seg=[f for f in u if f.day>=16]
    if md and len(u)==1: return "Mismo Día"
    if pri and not seg: return "Primera Quincena"
    if seg and not pri: return "Segunda Quincena"
    if pri and seg: return "Primera + Segunda"
    return "Sin Día"

def clasificar_seguimiento(obj_dt: Optional[datetime],
                           hab_dt: Optional[datetime],
                           ng_dt: Optional[datetime],
                           fobj: datetime) -> str:

    obj_v, hab_v, ng_v = en_vig(fobj, obj_dt), en_vig(fobj, hab_dt), en_vig(fobj, ng_dt)

    # Tratamiento mixto
    if hab_v and ng_v:
        return "Tratamiento mixto + Seguimiento" if obj_v else "Tratamiento mixto (GES+NG)"

    # Tratamiento + seguimiento
    if (hab_v or ng_v) and obj_v:
        return "Tratamiento + Seguimiento"

    # Tratamientos vigentes por separado
    if ng_v:  return "Tratamiento NG Vigente"
    if hab_v: return "Tratamiento GES Vigente"

    # Solo seguimiento vigente / antiguo
    if obj_v:  return "Seguimiento Reciente"
    if obj_dt: return "Seguimiento Antiguo"

    # Antiguos (no vigentes): elegir el más reciente y explicitar si es GES o NG
    if hab_dt or ng_dt:
        ult, tip = None, None
        if hab_dt and (not ult or hab_dt > ult): ult, tip = hab_dt, "GES"
        if ng_dt  and (not ult or ng_dt > ult): ult, tip = ng_dt,  "NG"
        return f"Tratamiento {tip} Antiguo"

    return "Caso Vacío"

def analizar_mision(sigges: SiggesDriver, m: Dict[str,Any], casos: List[str], fobj: datetime,
                    fexcel: str, fall_dt: Optional[datetime],
                    ng_global: bool, ng_txt: Optional[str], ng_dt: Optional[datetime]) -> Dict[str,Any]:
    usar_habs = m.get("usar_habilitantes", True)
    res = {"Fecha": fexcel, "Rut": "", "Nombre": "", "Caso Encontrado":"Sin caso","Objetivo":"N/A",
           "Hab?":"No","Habilitante":"","Fecha Hábil":"","Hab Vig?":"No","NG?":"No","NG Fecha":"","NG Vig?":"No",
           "Mensual":"Sin Día","Seguimiento":"Sin Caso"}
    objetivo, habs = m.get("objetivo"), (m.get("habilitantes",[]) if usar_habs else [])
    require_any, top_k, usar_ng = m.get("require_any",True), m.get("top_k",TOP_K_HABILITANTES), m.get("usar_ng",True)

    idx, texto, _ = elegir_caso_mas_reciente(casos, m["keywords"])
    if idx is None:
        # Sin caso para esta misión → se deja "Sin Caso" y NO se aplica NG
        return res

    res["Caso Encontrado"] = texto
    tbody = sigges.abrir_caso_por_indice(idx)
    if not tbody:
        sigges.cerrar_caso_por_indice(idx)
        return res
    prestaciones = sigges.leer_prestaciones_desde_tbody(tbody)
    sigges.cerrar_caso_por_indice(idx)

    if DEBUG_PRINT_CODES and prestaciones:
        try: log(CODE, "    DEBUG Códigos ⟶ " + ", ".join(f"{p['codigo']}@{p['fecha']}" for p in prestaciones))
        except: pass

    # Seguimiento (código objetivo)
    obj_dates, last_obj = [], None
    for p in prestaciones:
        if p.get("codigo")==objetivo:
            f = dparse(p.get("fecha",""))
            if f and f<=fobj:
                obj_dates.append(f)
                if (not last_obj) or f>last_obj: last_obj = f
    if last_obj: res["Objetivo"]=last_obj.strftime("%d/%m/%Y")
    res["Mensual"] = mensual_categoria([f for f in obj_dates if same_month(f, fobj)], fobj) if obj_dates else "Sin Día"

    # Habilitantes (si aplica)
    last_hab = None
    if usar_habs and habs:
        lst = listar_habilitantes(prestaciones, habs, fobj)
        res["Hab?"] = "Sí" if lst else "No"
        if lst:
            top = lst[:1] if require_any else lst[:top_k]
            res["Habilitante"] = " | ".join(c for c,_ in top)
            res["Fecha Hábil"] = " | ".join(d.strftime("%d/%m/%Y") for _,d in top)
            last_hab = lst[0][1]
            res["Hab Vig?"] = "Sí" if en_vig(fobj,last_hab) else "No"
    else:
        res["Hab?"] = "No"; res["Habilitante"] = ""; res["Fecha Hábil"] = ""; res["Hab Vig?"] = "No"

    # No GES (solo si la misión usa NG y hubo NG global detectado)
    if usar_ng and ng_global:
        res.update({"NG?":"Sí","NG Fecha":ng_txt or "","NG Vig?":"Sí" if en_vig(fobj,ng_dt) else "No"})

    # Clasificación global de seguimiento (para Excel)
    res["Seguimiento"] = clasificar_seguimiento(
    obj_dt=last_obj,
    hab_dt=last_hab,
    ng_dt=(ng_dt if usar_ng else None),
    fobj=fobj,
)

    # Logs (limpios)
    try:
        log(INFO, f"[{m['nombre']}] Caso: {res['Caso Encontrado']}")
        log(OK if res["Objetivo"]!="N/A" else WARN, f"    Seguimiento ⟶ {res['Objetivo'] if res['Objetivo']!='N/A' else 'ninguno'}")
        if usar_habs:
            if res["Hab?"]=="Sí":
                log(CODE, f"    Habilitante ⟶ {res['Habilitante']} @ {res['Fecha Hábil']}")
            else:
                log(WARN, "    Habilitante ⟶ ninguno")
        if m.get("usar_ng", True):
            log(DATA if res["NG?"]=="Sí" else WARN, f"    NG ⟶ {res['NG Fecha'] if res['NG?']=='Sí' else 'ninguno'}")
    except: pass
    return res

# ═════════════════════════════════════════════════════════════════════════════
# EXPORTACIÓN
# ═════════════════════════════════════════════════════════════════════════════

def cols_mision(m: Dict[str,Any]) -> List[str]:
    cols = ["Fecha","Rut","Nombre","Caso Encontrado","Objetivo"]
    if m.get("usar_habilitantes", True) and m.get("habilitantes"):
        cols += ["Hab?","Habilitante","Fecha Hábil","Hab Vig?"]
    if m.get("usar_ng", True):
        cols += ["NG?","NG Fecha","NG Vig?"]
    cols += ["Mensual","Seguimiento"]
    return cols

def cols_prefijo(i:int, m:Dict[str,Any])->List[str]:
    base=["Caso Encontrado","Objetivo"]
    if m.get("usar_habilitantes", True) and m.get("habilitantes"):
        base+=["Hab?","Habilitante","Fecha Hábil","Hab Vig?"]
    if m.get("usar_ng",True):
        base+=["NG?","NG Fecha","NG Vig?"]
    base+=["Mensual","Seguimiento"]; pref=f"M{i+1} "
    return [pref+c for c in base]

# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

def ejecutar_revision()->None:
    # Conecta a Edge ya abierto en modo debug
    opts = webdriver.EdgeOptions(); opts.debugger_address = DIRECCION_DEBUG_EDGE
    try: driver = webdriver.Edge(service=Service(EDGE_DRIVER_PATH), options=opts)
    except Exception as e: print(f"Error conectando a Edge: {e}"); return
    sigges = SiggesDriver(driver)

    # Lee Excel
    try: df = pd.read_excel(RUTA_ARCHIVO_ENTRADA)
    except Exception as e: print(f"Error leyendo Excel: {e}"); driver.quit(); return

    filas_por_mision: Dict[int,List[Dict[str,Any]]] = {i:[] for i in range(len(MISSIONS))}
    filas_conjuntas: List[Dict[str,Any]] = []
    total=len(df)

    for idx,row in df.iterrows():
        nombre = str(row.iloc[INDICE_COLUMNA_NOMBRE]).strip()
        rut    = str(row.iloc[INDICE_COLUMNA_RUT]).strip()
        fecha  = solo_fecha(row.iloc[INDICE_COLUMNA_FECHA])
        fobj   = dparse(fecha)

        # Encabezado al inicio (antes de Cartola)
        log(INFO, "────────────────────────────────────────────────────────")
        log(INFO, f"[{idx+1}/{total}] Paciente: {nombre} | RUT: {rut} | Fecha: {fecha}")

        # Buscar paciente en “búsqueda rápida”
        sigges.asegurar_en_busqueda()
        campo = sigges._find(["/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/div/div/input"], "presence", 20)
        if not campo:
            log(ERR, "Campo RUT no encontrado"); continue
        try: campo.clear()
        except StaleElementReferenceException:
            campo = sigges._find(["/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/div/div/input"], "presence", 10); campo.clear()
        campo.send_keys(rut)
        sigges._click(["/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/button"], scroll=False, wait_spinner=True)
        sigges.esperar_spinner()

        # Mini-tabla (filtrada)
        mini = []
        try: mini = leer_mini_tabla_busqueda(sigges.driver)
        except: pass

        # Imprimir mini-tabla según modo
        if MINI_TABLA_MODO != "oculto" and mini:
            def es_relevante(r): return any(has_keyword(r["problema"], m["keywords"]) for m in MISSIONS)
            filas = mini if MINI_TABLA_MODO=="detallado" else [r for r in mini if es_relevante(r)]
            for i, r in enumerate(filas,1):
                marca = " ✔" if es_relevante(r) else ""
                linea = f"  • {i}. {r['problema']} | {r.get('estado') or '—'}{marca}"
                log(OK if marca else WARN, linea)

        # ¿Hay al menos un caso relevante?
        tiene_relevante = any(
            has_keyword(r["problema"], m["keywords"])
            for r in (mini or [])
            for m in MISSIONS
        )

        # Si NO hay caso relevante ⇒ saltar Cartola, exportar “Sin caso” y seguir
        if not tiene_relevante:
            base_conjunta = {"Fecha":fecha,"Rut":rut,"Nombre":nombre}
            for i, m in enumerate(MISSIONS):
                vac = {
                    "Fecha":fecha,"Rut":rut,"Nombre":nombre,
                    "Caso Encontrado":"Sin caso","Objetivo":"N/A",
                    **({"Hab?":"No","Habilitante":"","Fecha Hábil":"","Hab Vig?":"No"} if m.get("usar_habilitantes", True) and m.get("habilitantes") else {}),
                    **({"NG?":"No","NG Fecha":"","NG Vig?":"No"} if m.get("usar_ng", True) else {}),
                    "Mensual":"Sin Día","Seguimiento":"Sin Caso",
                }
                filas_por_mision[i].append(vac)
                for col in cols_mision(m):
                    if col in ("Fecha","Rut","Nombre"): continue
                    base_conjunta[f"M{i+1} {col}"] = vac.get(col, "")
            filas_conjuntas.append(base_conjunta)
            log(INFO, "  → Sin caso relevante en mini-tabla. Se omite Cartola.")
            continue

        # Hay caso relevante ⇒ abrir Cartola
        if not sigges.ir_a_cartola():
            log(ERR, "No se pudo abrir la Cartola Unificada"); continue
        sigges.esperar_spinner(); time.sleep(SLEEP_LECTURA_TABLAS)
        sigges.activar_hitos_ges()

        # Estado de fallecimiento (solo informativo)
        fall_dt = sigges.leer_fallecimiento()
        log(WARN if fall_dt else INFO, f"{'Fallecido: ' + fall_dt.strftime('%d/%m/%Y') if fall_dt else 'Paciente Vivo'}")

        # Escanear NG solo si alguna misión lo usa (ya estamos en Cartola porque hay caso relevante)
        if any(m.get("usar_ng", True) for m in MISSIONS):
            ng_global, ng_txt, ng_dt = scan_no_ges(sigges.driver, fobj)
            if ng_global: log(DATA, f"Quimio NG detectada: {ng_txt}")
        else:
            ng_global, ng_txt, ng_dt = (False, None, None)

        # Casos en Cartola y análisis por misión
        time.sleep(SLEEP_LECTURA_TABLAS); casos = sigges.lista_de_casos_cartola()
        resultados_paciente: Dict[int, Dict[str,Any]] = {}
        for i, m in enumerate(MISSIONS):
            r = analizar_mision(sigges, m, casos, fobj, fecha, fall_dt, ng_global, ng_txt, ng_dt)
            r.update({"Fecha":fecha,"Rut":rut,"Nombre":nombre}); resultados_paciente[i]=r

        # Exportación
        for i in range(len(MISSIONS)): filas_por_mision[i].append(resultados_paciente[i])
        base={"Fecha":fecha,"Rut":rut,"Nombre":nombre}
        for i,m in enumerate(MISSIONS):
            r=resultados_paciente[i]
            for col in cols_mision(m):
                if col in ("Fecha","Rut","Nombre"): continue
                base[f"M{i+1} {col}"]=r.get(col,"")
        filas_conjuntas.append(base)

    # Exporta Excel
    if filas_conjuntas or any(filas_por_mision.values()):
        os.makedirs(RUTA_CARPETA_SALIDA, exist_ok=True)
        ts=datetime.now().strftime("%Y%m%d_%H%M")
        out=os.path.join(RUTA_CARPETA_SALIDA, f"Revision_{NOMBRE_DE_LA_MISION}_{ts}.xlsx")
        try:
            with pd.ExcelWriter(out, engine="openpyxl") as w:
                if HOJA_POR_MISION:
                    for i,m in enumerate(MISSIONS):
                        pd.DataFrame(filas_por_mision[i], columns=cols_mision(m)).to_excel(w, index=False, sheet_name=f"Mision {i+1}")
                else:
                    cols=["Fecha","Rut","Nombre"]
                    for i,m in enumerate(MISSIONS): cols += cols_prefijo(i,m)
                    pd.DataFrame(filas_conjuntas, columns=cols).to_excel(w, index=False, sheet_name="Detallado")
                # Hoja “Carga Masiva” vacía (molde fijo)
                pd.DataFrame([], columns=["FECHA","RUT","DV","PRESTACIONES","TIPO","PS-FAM","ESPECIALIDAD"]).to_excel(w, index=False, sheet_name="Carga Masiva")
            print(f"Archivo generado: {out}")
        except Exception as e:
            print(f"Error generando archivo de salida: {e}")

    driver.quit()

if __name__=="__main__":
    ejecutar_revision()
