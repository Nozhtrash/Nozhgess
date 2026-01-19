# -*- coding: utf-8 -*-
import os, re, time, unicodedata, gc
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
# PANEL DE CONTROL
# ═════════════════════════════════════════════════════════════════════════════

NOMBRE_DE_LA_MISION = "IAM"
RUTA_ARCHIVO_ENTRADA = r"C:\\Users\\Usuario HGF\\Desktop\\Trabajo\\IAM.xlsx"
RUTA_CARPETA_SALIDA  = r"C:\Users\Usuario HGF\Desktop\Trabajo\Revisiones"
DIRECCION_DEBUG_EDGE = "localhost:9222"
EDGE_DRIVER_PATH     = r"C:\\Windows\\System32\\msedgedriver.exe"

INDICE_COLUMNA_FECHA  = 0
INDICE_COLUMNA_RUT    = 2
INDICE_COLUMNA_NOMBRE = 4

# Reintentos / timing
MAXIMOS_REINTENTOS_POR_PACIENTE = 2
ESPERA_ENTRE_INTENTOS_SEG = 2
SLEEP_LECTURA_TABLAS = 0.5
VENTANA_VIGENCIA_DIAS = 90

# Spinner / tiempos
SPINNER_APPEAR_TIMEOUT = 1.5
SPINNER_DISAPPEAR_TIMEOUT = 25         # base
SPINNER_DISAPPEAR_TIMEOUT_LARGO = 120  # “modo tortuga”
SPINNER_SETTLE = 0.35
POST_BUSQUEDA_SLEEP = 0.8

# Mini-tabla
MINI_TABLA_REINTENTOS = 2
MINI_TABLA_SLEEP = 0.8
MINI_TABLA_STABLE_READS = 2

# Export
HOJA_POR_MISION = True

# Consola
MINI_TABLA_MODO = "compacto"
OMITIR_EVENTO_SIN_CASO = True
DEBUG_PRINT_CODES = False

# Interacción en errores graves
MODO_INTERACTIVO_ERRORES = True
MAX_REINTENTOS_GRAVES_POR_PACIENTE = 3
GC_CADA_N_PACIENTES = 60  # pasa GC para evitar tumores de memoria

TOP_K_HABILITANTES = 3

MISSIONS: List[Dict[str, Any]] = [
    {
        "nombre": "Artrosis de Rodilla",
        "keywords": ["rodilla", "artrosis de rodilla", "artrósis de cadera", "artrosis de cadera"],
        "objetivo": "0101111",
        "usar_habilitantes": False,
        "habilitantes": [],
        "require_any": True,
        "top_k": 1,
        "usar_ng": False,
    },
    {
        "nombre": "Endoprótesis",
        "keywords": ["endoprotesis", "endoprótesis", "endoprótesis de cadera" ],
        "objetivo": "0101111",
        "usar_habilitantes": True,
        "habilitantes": ["2104229", "2104329"],
        "require_any": True,
        "top_k": 1,
        "usar_ng": False,
    },
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
    try:
        print(color + msg + RESET)
    except:
        print(msg)

# ═════════════════════════════════════════════════════════════════════════════
# EXCEPCIONES CUSTOM
# ═════════════════════════════════════════════════════════════════════════════

class SpinnerStuck(Exception):
    """Spinner no desapareció a tiempo."""
    pass

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

def same_month(a: datetime, b: datetime) -> bool:
    return a.year==b.year and a.month==b.month

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
# NO GES (quimioterapia)
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
    def __init__(self, driver: webdriver.Remote) -> None:
        self.driver = driver

    def esperar_spinner(self, appear_timeout=SPINNER_APPEAR_TIMEOUT,
                        disappear_timeout=SPINNER_DISAPPEAR_TIMEOUT,
                        settle=SPINNER_SETTLE,
                        raise_on_timeout: bool = False) -> None:
        """Espera a que aparezca (si aparece) y desaparezca el spinner; añade aire (settle).
        Si raise_on_timeout=True, lanza SpinnerStuck si no desaparece a tiempo.
        """
        seen=False
        try:
            end = time.time()+appear_timeout
            while time.time()<end:
                if self.driver.find_elements(By.CSS_SELECTOR,"dialog.loading"):
                    seen=True; break
                time.sleep(0.05)
        except:
            seen=False
        if not seen:
            time.sleep(settle)
            return
        try:
            WebDriverWait(self.driver, disappear_timeout).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR,"dialog.loading"))
            )
        except TimeoutException:
            # aún está? entonces está pegado de verdad
            try:
                if self.driver.find_elements(By.CSS_SELECTOR,"dialog.loading"):
                    if raise_on_timeout:
                        raise SpinnerStuck(f"Spinner no desapareció en {disappear_timeout}s")
                # si no está, igual seguimos
            except:
                if raise_on_timeout:
                    raise SpinnerStuck(f"Spinner timeout (y no se pudo verificar estado)")
        time.sleep(settle)

    def _find(self, xps: List[str], mode="clickable", timeout=3) -> Optional[Any]:
        for xp in xps:
            try:
                cond = {"presence":EC.presence_of_element_located, "visible":EC.visibility_of_element_located}.get(mode, EC.element_to_be_clickable)
                return WebDriverWait(self.driver, timeout).until(cond((By.XPATH,xp)))
            except:
                continue
        return None

    def _click(self, xps: List[str], scroll=True, wait_spinner=False, raise_on_spinner_timeout=False,
               spinner_timeout=SPINNER_DISAPPEAR_TIMEOUT) -> bool:
        el = self._find(xps,"clickable",3)
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
        if wait_spinner:
            self.esperar_spinner(disappear_timeout=spinner_timeout, raise_on_timeout=raise_on_spinner_timeout)
        return True

    def asegurar_en_busqueda(self) -> None:
        try:
            if "actualizaciones" in self.driver.current_url:
                self.driver.get("https://www.sigges.cl/#/busqueda-de-paciente")
                self.esperar_spinner(raise_on_timeout=False)
        except:
            pass
        if self._find(["/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/div/div/input"],"presence",2):
            return
        self._click(["/html/body/div/main/div[2]/nav/div[1]/div[2]/a[1]"], scroll=False, wait_spinner=True)

    def ir_a_cartola(self, spinner_timeout=SPINNER_DISAPPEAR_TIMEOUT, raise_on_spinner_timeout=True) -> bool:
        return self._click(
            ["/html/body/div/main/div[2]/nav/div[1]/div[2]/a[4]"],
            scroll=False, wait_spinner=True,
            raise_on_spinner_timeout=raise_on_spinner_timeout,
            spinner_timeout=spinner_timeout
        )

    def activar_hitos_ges(self) -> None:
        chk = self._find(["/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div/div/label/input"], "presence", 20)
        if not chk: return
        try:
            if not chk.is_selected():
                self._click(["/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div/div/label/input"], True, True)
        except: pass
        root = self._find(["/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]"], "presence", 5)
        end = time.time()+2
        while time.time()<end:
            try:
                if root and root.find_elements(By.CSS_SELECTOR,"div.contRow"): return
            except: pass
            time.sleep(0.25)

    def lista_de_casos_cartola(self) -> List[str]:
        time.sleep(SLEEP_LECTURA_TABLAS)
        root = self._find(["/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]"], "presence", 5)
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
        try:
            self._click([f"({base})/div[{n}]/div/label/input", f"({base})/div[{n}]"], wait_spinner=False)
            time.sleep(0.3)
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
# MINI TABLA
# ═════════════════════════════════════════════════════════════════════════════

XPATH_MINI_TBODY_CANDIDATES = [
    "/html/body/div/main/div[3]/div[3]/div/div[2]/div/div/table/tbody",
    "//div[@class='contBody maxW scroll']//div[contains(@class,'cardTable')]/table/tbody",
]

def leer_mini_tabla_busqueda(driver: Any, timeout=8.0, stable_reads=MINI_TABLA_STABLE_READS) -> List[Dict[str,str]]:
    tbody=None
    for xp in XPATH_MINI_TBODY_CANDIDATES:
        try:
            tbody = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH,xp)))
            break
        except:
            continue
    if not tbody:
        return []

    end = time.time() + timeout
    last_key = None
    stable = 0
    last_snap: List[Dict[str,str]] = []

    while time.time() < end:
        try:
            snap = driver.execute_script("""
                const tb = arguments[0];
                if (!tb) return [];
                const rows = Array.from(tb.querySelectorAll('tr'));
                return rows.map(tr => {
                    const tds = tr.querySelectorAll('td');
                    if (tds.length < 4) return null;
                    const problema = tds[1].innerText.trim();
                    const decreto  = tds[2].innerText.trim();
                    const estado   = tds[3].innerText.trim();
                    return {problema, decreto, estado};
                }).filter(Boolean);
            """, tbody) or []
        except Exception:
            snap = []

        key = "|".join(f"{r['problema']}||{r['estado']}" for r in snap)

        if key and key == last_key:
            stable += 1
            if stable >= stable_reads:
                out = snap
                if OMITIR_EVENTO_SIN_CASO:
                    out = [r for r in out if "evento sin caso" not in _norm(r["problema"])]
                return out
        else:
            stable = 0
            last_key = key
            last_snap = snap

        time.sleep(0.25)

    out = last_snap
    if OMITIR_EVENTO_SIN_CASO:
        out = [r for r in out if "evento sin caso" not in _norm(r["problema"])]
    return out

# ═════════════════════════════════════════════════════════════════════════════
# LÓGICA DE MISIONES
# ═════════════════════════════════════════════════════════════════════════════

def elegir_caso_mas_reciente(casos: List[str], kws: List[str]) -> Tuple[Optional[int], Optional[str], Optional[datetime]]:
    best_i, best_t, best_f = None, None, None
    for i, t in enumerate(casos):
        if not has_keyword(t, kws): continue
        m=_ddmmyyyy.search(t); f = dparse(m.group(1)) if m else None
        if best_f is None or (f and f>best_f):
            best_i, best_t, best_f = i, (t.strip() if t else ""), (f or best_f)
    return best_i, best_t, best_f

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

    if hab_v and ng_v:
        return "Tratamiento mixto + Seguimiento" if obj_v else "Tratamiento mixto (GES+NG)"
    if (hab_v or ng_v) and obj_v:
        return "Tratamiento + Seguimiento"
    if ng_v:  return "Tratamiento NG Vigente"
    if hab_v: return "Tratamiento GES Vigente"
    if obj_v:  return "Seguimiento Reciente"
    if obj_dt: return "Seguimiento Antiguo"
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

    obj_dates, last_obj = [], None
    for p in prestaciones:
        if p.get("codigo")==objetivo:
            f = dparse(p.get("fecha",""))
            if f and (not fobj or f <= fobj):

                obj_dates.append(f)
                if (not last_obj) or f>last_obj: last_obj = f
    if obj_dates and fobj:
        res["Mensual"] = mensual_categoria([f for f in obj_dates if same_month(f, fobj)], fobj)
    else:
        res["Mensual"] = "Sin Día"

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

    if usar_ng and ng_global:
        res.update({"NG?":"Sí","NG Fecha":ng_txt or "","NG Vig?":"Sí" if en_vig(fobj,ng_dt) else "No"})

    res["Seguimiento"] = clasificar_seguimiento(
        obj_dt=last_obj,
        hab_dt=last_hab,
        ng_dt=(ng_dt if usar_ng else None),
        fobj=fobj,
    )

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
# INTERACCIÓN EN ERRORES GRAVES
# ═════════════════════════════════════════════════════════════════════════════

def prompt_interactivo(paciente_idx: int, rut: str, nombre: str, err: Exception) -> str:
    """Devuelve: 'retry' | 'skip' | 'slow' | 'refresh' | 'quit'"""
    if not MODO_INTERACTIVO_ERRORES:
        return 'skip'
    print()
    log(ERR, f"⚠️ Error en paciente #{paciente_idx}: {nombre} (RUT {rut})")
    log(ERR, f"   Tipo: {type(err).__name__} | {str(err)[:300]}")
    print()
    print("Opciones → [Enter]=Reintentar  |  *=Saltar  |  +=Modo tortuga  |  r=Refresh  |  q=Salir")
    try:
        ans = input("Tu elección: ").strip().lower()
    except KeyboardInterrupt:
        return 'quit'
    if ans == "": return 'retry'
    if ans == "*": return 'skip'
    if ans == "+": return 'slow'
    if ans == "r": return 'refresh'
    if ans == "q": return 'quit'
    return 'retry'

# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

def ejecutar_revision()->None:
    # Conecta a Edge ya abierto en modo debug
    opts = webdriver.EdgeOptions(); opts.debugger_address = DIRECCION_DEBUG_EDGE
    try:
        driver = webdriver.Edge(service=Service(EDGE_DRIVER_PATH), options=opts)
    except Exception as e:
        print(f"Error conectando a Edge: {e}"); return

    sigges = SiggesDriver(driver)

    # Lee Excel
    try:
        df = pd.read_excel(RUTA_ARCHIVO_ENTRADA)
    except Exception as e:
        print(f"Error leyendo Excel: {e}"); driver.quit(); return

    filas_por_mision: Dict[int,List[Dict[str,Any]]] = {i:[] for i in range(len(MISSIONS))}
    filas_conjuntas: List[Dict[str,Any]] = []
    total=len(df)

    for idx,row in df.iterrows():
        # GC periódica para sesiones largas
        if GC_CADA_N_PACIENTES and (idx>0) and (idx % GC_CADA_N_PACIENTES == 0):
            try:
                gc.collect()
                log(INFO, f"🧹 GC pasada en paciente #{idx}")
            except: pass

        nombre = str(row.iloc[INDICE_COLUMNA_NOMBRE]).strip()
        rut    = str(row.iloc[INDICE_COLUMNA_RUT]).strip()
        fecha  = solo_fecha(row.iloc[INDICE_COLUMNA_FECHA])
        fobj   = dparse(fecha)

        log(INFO, "────────────────────────────────────────────────────────")
        log(INFO, f"[{idx+1}/{total}] Paciente: {nombre} | RUT: {rut} | Fecha: {fecha}")

        # spinner timeout dinámico por paciente (puede subir con '+')
        spinner_timeout_actual = SPINNER_DISAPPEAR_TIMEOUT

        intentos_graves = 0
        while True:
            try:
                # Buscar paciente
                sigges.asegurar_en_busqueda()
                campo = sigges._find(["/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/div/div/input"], "presence", 20)
                if not campo:
                    raise TimeoutException("Campo RUT no encontrado en pantalla de búsqueda")
                try:
                    campo.clear()
                except StaleElementReferenceException:
                    campo = sigges._find(["/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/div/div/input"], "presence", 10)
                    campo.clear()
                campo.send_keys(rut)

                # Click Buscar con watchdog de spinner
                sigges._click(
                    ["/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/button"],
                    scroll=False, wait_spinner=True, raise_on_spinner_timeout=True,
                    spinner_timeout=spinner_timeout_actual
                )
                # spinner “tardío”
                sigges.esperar_spinner(disappear_timeout=spinner_timeout_actual, raise_on_timeout=True)
                time.sleep(POST_BUSQUEDA_SLEEP)

                # Mini-tabla con reintentos
                mini: List[Dict[str,str]] = []
                tiene_relevante = False
                for intento in range(MINI_TABLA_REINTENTOS + 1):
                    sigges.esperar_spinner(disappear_timeout=spinner_timeout_actual, raise_on_timeout=False)
                    try:
                        mini = leer_mini_tabla_busqueda(sigges.driver)
                    except:
                        mini = []
                    tiene_relevante = any(
                        has_keyword(r["problema"], m["keywords"])
                        for r in (mini or [])
                        for m in MISSIONS
                    )
                    if tiene_relevante or intento == MINI_TABLA_REINTENTOS:
                        break
                    time.sleep(MINI_TABLA_SLEEP)

                if MINI_TABLA_MODO != "oculto" and mini:
                    def es_relevante(r): return any(has_keyword(r["problema"], m["keywords"]) for m in MISSIONS)
                    filas = mini if MINI_TABLA_MODO=="detallado" else [r for r in mini if es_relevante(r)]
                    for i2, r2 in enumerate(filas,1):
                        marca = " ✔" if es_relevante(r2) else ""
                        linea = f"  • {i2}. {r2['problema']} | {r2.get('estado') or '—'}{marca}"
                        log(OK if marca else WARN, linea)

                if not tiene_relevante:
                    base_conjunta = {"Fecha":fecha,"Rut":rut,"Nombre":nombre}
                    for i_m, m in enumerate(MISSIONS):
                        vac = {
                            "Fecha":fecha,"Rut":rut,"Nombre":nombre,
                            "Caso Encontrado":"Sin caso","Objetivo":"N/A",
                            **({"Hab?":"No","Habilitante":"","Fecha Hábil":"","Hab Vig?":"No"} if m.get("usar_habilitantes", True) and m.get("habilitantes") else {}),
                            **({"NG?":"No","NG Fecha":"","NG Vig?":"No"} if m.get("usar_ng", True) else {}),
                            "Mensual":"Sin Día","Seguimiento":"Sin Caso",
                        }
                        filas_por_mision[i_m].append(vac)
                        # Construcción detallada
                        cols = ["Fecha","Rut","Nombre","Caso Encontrado","Objetivo"]
                        if m.get("usar_habilitantes", True) and m.get("habilitantes"):
                            cols += ["Hab?","Habilitante","Fecha Hábil","Hab Vig?"]
                        if m.get("usar_ng", True):
                            cols += ["NG?","NG Fecha","NG Vig?"]
                        cols += ["Mensual","Seguimiento"]
                        for col in cols:
                            if col in ("Fecha","Rut","Nombre"): continue
                            base_conjunta[f"M{i_m+1} {col}"] = vac.get(col, "")
                    filas_conjuntas.append(base_conjunta)
                    log(INFO, "  → Sin caso relevante en mini-tabla (tras reintentos). Se omite Cartola.")
                    break  # paciente listo (sin caso)

                # Ir a Cartola con watchdog fuerte
                if not sigges.ir_a_cartola(spinner_timeout=spinner_timeout_actual, raise_on_spinner_timeout=True):
                    raise TimeoutException("No se pudo abrir la Cartola Unificada (clic falló)")

                sigges.esperar_spinner(disappear_timeout=spinner_timeout_actual, raise_on_timeout=True)
                time.sleep(SLEEP_LECTURA_TABLAS)
                sigges.activar_hitos_ges()

                # Fallecimiento
                fall_dt = sigges.leer_fallecimiento()
                log(WARN if fall_dt else INFO, f"{'Fallecido: ' + fall_dt.strftime('%d/%m/%Y') if fall_dt else 'Paciente Vivo'}")

                # NG global
                if any(m.get("usar_ng", True) for m in MISSIONS):
                    ng_global, ng_txt, ng_dt = scan_no_ges(sigges.driver, fobj)
                    if ng_global: log(DATA, f"Quimio NG detectada: {ng_txt}")
                else:
                    ng_global, ng_txt, ng_dt = (False, None, None)

                time.sleep(SLEEP_LECTURA_TABLAS); casos = sigges.lista_de_casos_cartola()
                resultados_paciente: Dict[int, Dict[str,Any]] = {}
                for i_m, m in enumerate(MISSIONS):
                    r = analizar_mision(sigges, m, casos, fobj, fecha, fall_dt, ng_global, ng_txt, ng_dt)
                    r.update({"Fecha":fecha,"Rut":rut,"Nombre":nombre}); resultados_paciente[i_m]=r

                for i_m in range(len(MISSIONS)): filas_por_mision[i_m].append(resultados_paciente[i_m])
                base={"Fecha":fecha,"Rut":rut,"Nombre":nombre}
                for i_m,m in enumerate(MISSIONS):
                    r=resultados_paciente[i_m]
                    for col in cols_mision(m):
                        if col in ("Fecha","Rut","Nombre"): continue
                        base[f"M{i_m+1} {col}"]=r.get(col,"")
                filas_conjuntas.append(base)

                # Paciente procesado con éxito
                break

            except SpinnerStuck as e:
                intentos_graves += 1
                decision = prompt_interactivo(idx+1, rut, nombre, e)
                if decision == 'retry':
                    time.sleep(ESPERA_ENTRE_INTENTOS_SEG); continue
                if decision == 'slow':
                    spinner_timeout_actual = min(spinner_timeout_actual * 2, SPINNER_DISAPPEAR_TIMEOUT_LARGO)
                    log(WARN, f"⏳ Modo tortuga ON. Nuevo timeout spinner: {spinner_timeout_actual}s")
                    continue
                if decision == 'refresh':
                    try:
                        driver.refresh(); time.sleep(2)
                    except: pass
                    continue
                if decision == 'quit':
                    log(ERR, "Abortado por el usuario."); driver.quit(); return
                # skip
                log(WARN, "Saltando paciente por spinner pegado.")
                break

            except (TimeoutException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException) as e:
                intentos_graves += 1
                decision = prompt_interactivo(idx+1, rut, nombre, e)
                if decision == 'retry':
                    time.sleep(ESPERA_ENTRE_INTENTOS_SEG); continue
                if decision == 'slow':
                    spinner_timeout_actual = min(spinner_timeout_actual * 2, SPINNER_DISAPPEAR_TIMEOUT_LARGO)
                    log(WARN, f"⏳ Modo tortuga ON. Nuevo timeout spinner: {spinner_timeout_actual}s")
                    continue
                if decision == 'refresh':
                    try:
                        driver.refresh(); time.sleep(2)
                    except: pass
                    continue
                if decision == 'quit':
                    log(ERR, "Abortado por el usuario."); driver.quit(); return
                log(WARN, "Saltando paciente por error recuperable.")
                break

            except KeyboardInterrupt:
                log(ERR, "Interrumpido manualmente (Ctrl+C)."); driver.quit(); return

            except Exception as e:
                intentos_graves += 1
                decision = prompt_interactivo(idx+1, rut, nombre, e)
                if decision == 'retry':
                    time.sleep(ESPERA_ENTRE_INTENTOS_SEG); continue
                if decision == 'slow':
                    spinner_timeout_actual = min(spinner_timeout_actual * 2, SPINNER_DISAPPEAR_TIMEOUT_LARGO)
                    log(WARN, f"⏳ Modo tortuga ON. Nuevo timeout spinner: {spinner_timeout_actual}s")
                    continue
                if decision == 'refresh':
                    try:
                        driver.refresh(); time.sleep(2)
                    except: pass
                    continue
                if decision == 'quit':
                    log(ERR, "Abortado por el usuario."); driver.quit(); return
                log(WARN, "Saltando paciente por error inesperado.")
                break

            finally:
                if intentos_graves > MAX_REINTENTOS_GRAVES_POR_PACIENTE:
                    log(WARN, f"Demasiados intentos fallidos para {nombre}. Saltando.")
                    break

    # Exporta Excel
    if filas_conjuntas or any(filas_por_mision.values()):
        os.makedirs(RUTA_CARPETA_SALIDA, exist_ok=True)
        ts=datetime.now().strftime("%Y%m%d_%H%M")
        out=os.path.join(RUTA_CARPETA_SALIDA, f"Revision_{NOMBRE_DE_LA_MISION}_{ts}.xlsx")
        try:
            with pd.ExcelWriter(out, engine="openpyxl") as w:
                if HOJA_POR_MISION:
                    for i_m,m in enumerate(MISSIONS):
                        pd.DataFrame(filas_por_mision[i_m], columns=cols_mision(m)).to_excel(w, index=False, sheet_name=f"Mision {i_m+1}")
                else:
                    cols=["Fecha","Rut","Nombre"]
                    for i_m,m in enumerate(MISSIONS): cols += cols_prefijo(i_m,m)
                    pd.DataFrame(filas_conjuntas, columns=cols).to_excel(w, index=False, sheet_name="Detallado")
                pd.DataFrame([], columns=["FECHA","RUT","DV","PRESTACIONES","TIPO","PS-FAM","ESPECIALIDAD"]).to_excel(w, index=False, sheet_name="Carga Masiva")
            print(f"Archivo generado: {out}")
        except Exception as e:
            print(f"Error generando archivo de salida: {e}")

    driver.quit()

if __name__=="__main__":
    ejecutar_revision()
