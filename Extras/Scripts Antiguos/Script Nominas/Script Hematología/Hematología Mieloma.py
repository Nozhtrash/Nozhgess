# -*- coding: utf-8 -*-
import os, re, time, unicodedata, gc
from datetime import datetime
from typing import List, Optional, Dict, Tuple, Any, Callable

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
# PANEL DE CONTROL (ajusta solo aquí)
# ═════════════════════════════════════════════════════════════════════════════

# Rutas / conexión
NOMBRE_DE_LA_MISION   = "Hematologia"
RUTA_ARCHIVO_ENTRADA  = r"C:\Users\usuariohgf\OneDrive\Documentos\Trabajo Oficina\Archivos\Nóminas\2\ICEP 2° Quincena - Hematología (144) - Diciembre.xlsx"
RUTA_CARPETA_SALIDA   = r"C:\Users\usuariohgf\OneDrive\Documentos\Trabajo Oficina\Revisiones, Falta Enviar, CM, Listos\Revisiones\Revisiones Nóminas"
DIRECCION_DEBUG_EDGE  = "localhost:9222"
EDGE_DRIVER_PATH      = r"C:\\Windows\\System32\\msedgedriver.exe"

# Excel (0-based)
INDICE_COLUMNA_FECHA  = 10
INDICE_COLUMNA_RUT    = 1
INDICE_COLUMNA_NOMBRE = 2  # solo para logs

# Reintentos / timing
MAXIMOS_REINTENTOS_POR_PACIENTE   = 2
REINTENTOS_PASO                   = 3
ESPERA_ENTRE_INTENTOS_SEG         = 2
ESPERA_REINTENTOS_PASO            = 5
SLEEP_LECTURA_TABLAS              = 0.8
VENTANA_VIGENCIA_DIAS             = 90

# Spinner / tiempos
SPINNER_APPEAR_TIMEOUT            = 1.5
SPINNER_DISAPPEAR_TIMEOUT         = 25
SPINNER_DISAPPEAR_TIMEOUT_LARGO   = 120
SPINNER_SETTLE                    = 0.5
POST_BUSQUEDA_SLEEP               = 0.8

# Mini-tabla
MINI_TABLA_REINTENTOS             = 2
MINI_TABLA_SLEEP                  = 0.8
MINI_TABLA_STABLE_READS           = 2

# Export
HOJA_POR_MISION                   = True  # ⇦ pedido del jefe

# Consola / logging
MINI_TABLA_MODO                   = "compacto"  # "oculto" | "compacto" | "detallado"
OMITIR_EVENTO_SIN_CASO            = True
DEBUG_PRINT_CODES                 = False

# Interacción
MODO_INTERACTIVO_ERRORES          = True
MAX_REINTENTOS_GRAVES_POR_PACIENTE= 3
GC_CADA_N_PACIENTES               = 60

# Habilitantes
TOP_K_HABILITANTES                = 3

# Familias y especialidad por misión (según tu instrucción)
FAMILIA_POR_MISION = {
    "Linfoma": "17",
    "Mieloma": "84",
}
ESPECIALIDAD_POR_MISION = {
    "Linfoma": "07-107-2",
    "Mieloma": "07-107-2",
}

# ── Misiones Hematología ─────────────────────────────────────────────────────
# Mantiene extras: habilitantes + NG (quimio)
MISSIONS: List[Dict[str, Any]] = [
    {
        "nombre": "Mieloma",
        "keywords": ["mieloma", "mieloma multiple", "mieloma múltiple", "mieloma múltiple  ."],
        "objetivo": "2506084",
        "usar_habilitantes": True,
        "habilitantes": ["2505917","2505918","2505920","2505921","2505924","2505925","2505927","2505929","2902004","2902008","2506083"],
        "require_any": False,
        "top_k": 3,
        "usar_ng": True,
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
# EXCEPCIÓN CUSTOM
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

def join_tags(tags: List[str]) -> str:
    tags = [t.strip() for t in tags if t and str(t).strip()]
    return " + ".join(tags)

# ═════════════════════════════════════════════════════════════════════════════
# NO GES (Quimioterapia)
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
# SELENIUM WRAPPER (robusto)
# ═════════════════════════════════════════════════════════════════════════════
class SiggesDriver:
    def __init__(self, driver: webdriver.Remote) -> None:
        self.driver = driver

    def esperar_spinner(self, appear_timeout=SPINNER_APPEAR_TIMEOUT,
                        disappear_timeout=SPINNER_DISAPPEAR_TIMEOUT,
                        settle=SPINNER_SETTLE,
                        raise_on_timeout: bool = False) -> None:
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
            try:
                if self.driver.find_elements(By.CSS_SELECTOR,"dialog.loading"):
                    if raise_on_timeout:
                        raise SpinnerStuck(f"Spinner no desapareció en {disappear_timeout}s")
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

    def _click(self, xps: List[str], scroll=True, wait_spinner=False,
               raise_on_spinner_timeout=False, spinner_timeout=SPINNER_DISAPPEAR_TIMEOUT) -> bool:
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

    # Navegación
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

    # Casos (Cartola)
    def abrir_caso_por_indice(self, i:int) -> Optional[Any]:
        n = i+1; base = "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]"
        if not self._click([f"({base})/div[{n}]/div/label/input", f"({base})/div[{n}]"], wait_spinner=False): return None
        time.sleep(0.3)
        try:
            return WebDriverWait(self.driver,14).until(EC.presence_of_element_located((By.XPATH, f"({base})/div[{n}]/div[6]/div[2]/div/table/tbody")))
        except TimeoutException:
            return None

    def cerrar_caso_por_indice(self, i:int)->None:
        n=i+1; base="/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]"
        try:
            self._click([f"({base})/div[{n}]/div/label/input", f"({base})/div[{n}]"], wait_spinner=False)
            time.sleep(0.3)
        except: pass

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
# LÓGICA DE MISIONES (con habilitantes + NG)
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

    nombre_m = m["nombre"]
    objetivo = m.get("objetivo","")
    usar_habs = m.get("usar_habilitantes", True)

    # Base con orden EXACTO de Reumatología (manteniendo extras al final)
    res = {
        "Fecha": fexcel,
        "Rut": "",
        "Cod Objetivo": objetivo,
        "Familia": FAMILIA_POR_MISION.get(nombre_m,""),
        "Especialidad": ESPECIALIDAD_POR_MISION.get(nombre_m,""),
        "Caso Encontrado":"Sin caso",
        "Objetivo":"N/A",
        "Mensual":"Sin Día",
        "Seguimiento":"Sin Caso",
        "Fecha IPD":"", "Estado IPD":"", "Diagnóstico IPD":"",  # Hemato no usa IPD: quedan vacíos
        "Observación":"",

        # Extras Hemato (van DESPUÉS de Observación para no romper el orden base)
        "Hab?":"No","Habilitante":"","Fecha Hábil":"","Hab Vig?":"No",
        "NG?":"No","NG Fecha":"","NG Vig?":"No",
    }

    idx, texto, _ = elegir_caso_mas_reciente(casos, m["keywords"])
    if idx is None:
        res["Observación"] = "Sin caso relevante en mini-tabla"
        return res

    res["Caso Encontrado"] = texto

    # Abrir caso y leer prestaciones
    tbody = sigges.abrir_caso_por_indice(idx)
    if not tbody:
        sigges.cerrar_caso_por_indice(idx)
        res["Observación"] = "No se pudo abrir el caso"
        return res

    prestaciones = sigges.leer_prestaciones_desde_tbody(tbody)
    sigges.cerrar_caso_por_indice(idx)

    if DEBUG_PRINT_CODES and prestaciones:
        try: log(CODE, "    DEBUG Códigos ⟶ " + ", ".join(f"{p['codigo']}@{p['fecha']}" for p in prestaciones))
        except: pass

    # Objetivo (seguimiento)
    obj_dates, last_obj = [], None
    for p in prestaciones:
        if p.get("codigo")==objetivo:
            f = dparse(p.get("fecha",""))
            if f and f<=fobj:
                obj_dates.append(f)
                if (not last_obj) or f>last_obj: last_obj = f
    if last_obj: res["Objetivo"]=last_obj.strftime("%d/%m/%Y")
    res["Mensual"] = mensual_categoria([f for f in obj_dates if same_month(f, fobj)], fobj) if obj_dates else "Sin Día"

    # Habilitantes
    last_hab = None
    if usar_habs and m.get("habilitantes"):
        lst = listar_habilitantes(prestaciones, m["habilitantes"], fobj)
        res["Hab?"] = "Sí" if lst else "No"
        if lst:
            top = lst[:1] if m.get("require_any",True) else lst[:m.get("top_k",TOP_K_HABILITANTES)]
            res["Habilitante"] = " | ".join(c for c,_ in top)
            res["Fecha Hábil"] = " | ".join(d.strftime("%d/%m/%Y") for _,d in top)
            last_hab = lst[0][1]
            res["Hab Vig?"] = "Sí" if en_vig(fobj,last_hab) else "No"

    # NG (quimio)
    if m.get("usar_ng", True) and ng_global:
        res.update({"NG?":"Sí","NG Fecha":ng_txt or "","NG Vig?":"Sí" if en_vig(fobj,ng_dt) else "No"})

    # Clasificador global
    res["Seguimiento"] = clasificar_seguimiento(
        obj_dt=last_obj,
        hab_dt=last_hab,
        ng_dt=(ng_dt if m.get("usar_ng",True) else None),
        fobj=fobj,
    )

    # Observación (concisa, estilo reuma)
    obs: List[str] = []
    if fall_dt: obs.append(f"Fallecido {fall_dt.strftime('%d/%m/%Y')}")
    if not last_obj: obs.append("Sin Objetivo")
    if res["Hab?"] == "No" and m.get("habilitantes"): obs.append("Sin Habilitante")
    res["Observación"] = join_tags(obs)

    # Logs
    try:
        log(INFO, f"[{m['nombre']}] Caso: {res['Caso Encontrado']}")
        log(OK if res["Objetivo"]!="N/A" else WARN, f"    Seguimiento ⟶ {res['Objetivo'] if res['Objetivo']!='N/A' else 'ninguno'}")
        if m.get("habilitantes"):
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
#  Orden BASE = Reumatología:
#  ["Fecha","Rut","Cod Objetivo","Familia","Especialidad","Caso Encontrado",
#   "Objetivo","Mensual","Seguimiento","Fecha IPD","Estado IPD","Diagnóstico IPD","Observación"]
#  + Extras Hemato al final: ["Hab?","Habilitante","Fecha Hábil","Hab Vig?","NG?","NG Fecha","NG Vig?"]
# ═════════════════════════════════════════════════════════════════════════════
def cols_mision(m: Dict[str,Any]) -> List[str]:
    base = [
        "Fecha","Rut","Cod Objetivo","Familia","Especialidad",
        "Caso Encontrado","Objetivo","Mensual","Seguimiento",
        "Fecha IPD","Estado IPD","Diagnóstico IPD","Observación"
    ]
    extras = []
    if m.get("usar_habilitantes", True) and m.get("habilitantes"):
        extras += ["Hab?","Habilitante","Fecha Hábil","Hab Vig?"]
    if m.get("usar_ng", True):
        extras += ["NG?","NG Fecha","NG Vig?"]
    return base + extras

def cols_prefijo(i:int, m:Dict[str,Any])->List[str]:
    # Solo se usa si HOJA_POR_MISION=False, se conserva por compat.
    base=[
        "Cod Objetivo","Familia","Especialidad",
        "Caso Encontrado","Objetivo","Mensual","Seguimiento",
        "Fecha IPD","Estado IPD","Diagnóstico IPD","Observación"
    ]
    if m.get("usar_habilitantes", True) and m.get("habilitantes"):
        base += ["Hab?","Habilitante","Fecha Hábil","Hab Vig?"]
    if m.get("usar_ng",True):
        base += ["NG?","NG Fecha","NG Vig?"]
    pref=f"M{i+1} "
    return [pref+c for c in base]

# ═════════════════════════════════════════════════════════════════════════════
# REINTENTOS DE PASO + PAUSA INTERACTIVA
# ═════════════════════════════════════════════════════════════════════════════
def pausa_usuario(msg: str) -> str:
    print()
    log(ERR, msg)
    print("↪ Opciones: [Enter]=Reintentar  |  *=Saltar paciente  |  q=Salir")
    try:
        ans = input("Tu elección: ").strip().lower()
    except KeyboardInterrupt:
        return 'q'
    if ans == "": return 'retry'
    if ans == "*": return 'skip'
    if ans == "q": return 'quit'
    return 'retry'

def intentar_paso(nombre_paso: str, fn: Callable[[], Any]) -> Tuple[bool, Any]:
    for intento in range(1, REINTENTOS_PASO+1):
        try:
            res = fn()
            return True, res
        except Exception as e:
            log(WARN, f"[{nombre_paso}] Error intento {intento}/{REINTENTOS_PASO}: {type(e).__name__}: {str(e)[:120]}")
            time.sleep(ESPERA_REINTENTOS_PASO)
    accion = pausa_usuario(f"[{nombre_paso}] Falló {REINTENTOS_PASO} veces. ¿Qué hacemos?")
    if accion == 'retry':
        try:
            res = fn()
            return True, res
        except Exception as e:
            log(ERR, f"[{nombre_paso}] Falló nuevamente tras Enter: {type(e).__name__}: {str(e)[:120]}")
            return False, None
    elif accion == 'skip':
        return False, "SKIP"
    else:
        raise KeyboardInterrupt("Salida solicitada por el usuario")

# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════
def ejecutar_revision()->None:
    # Conecta a Edge en modo debug
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
        # GC periódica
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

        spinner_timeout_actual = SPINNER_DISAPPEAR_TIMEOUT
        intentos_graves = 0

        while True:
            try:
                # 1) Búsqueda
                ok, _ = intentar_paso("Ir a búsqueda", lambda: (sigges.asegurar_en_busqueda() or True))
                if not ok:
                    if _ == "SKIP":
                        base_conjunta = {"Fecha":fecha,"Rut":rut}
                        for i_m, m in enumerate(MISSIONS):
                            vac = {
                                "Fecha":fecha,"Rut":rut,
                                "Cod Objetivo": m.get("objetivo",""),
                                "Familia": FAMILIA_POR_MISION.get(m["nombre"],""),
                                "Especialidad": ESPECIALIDAD_POR_MISION.get(m["nombre"],""),
                                "Caso Encontrado":"Paciente Saltado","Objetivo":"N/A",
                                "Mensual":"Sin Día","Seguimiento":"Saltado",
                                "Fecha IPD":"", "Estado IPD":"", "Diagnóstico IPD":"", "Observación":"Paciente Saltado",
                            }
                            if m.get("habilitantes"): vac.update({"Hab?":"No","Habilitante":"","Fecha Hábil":"","Hab Vig?":"No"})
                            if m.get("usar_ng", True): vac.update({"NG?":"No","NG Fecha":"","NG Vig?":"No"})
                            filas_por_mision[i_m].append(vac)
                            for col in cols_mision(m):
                                if col in ("Fecha","Rut"): continue
                                base_conjunta[f"M{i_m+1} {col}"] = vac.get(col, "")
                        filas_conjuntas.append(base_conjunta)
                        break
                    else:
                        raise TimeoutException("No se pudo ir a búsqueda")

                def escribir_rut():
                    el = sigges._find(["/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/div/div/input"], "presence", 20)
                    if not el: raise TimeoutException("Campo RUT no encontrado")
                    try: el.clear()
                    except StaleElementReferenceException:
                        el = sigges._find(["/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/div/div/input"], "presence", 10); el.clear()
                    el.send_keys(rut); return True
                ok, res = intentar_paso("Escribir RUT", escribir_rut)
                if not ok:
                    if res=="SKIP":
                        base_conjunta = {"Fecha":fecha,"Rut":rut}
                        for i_m, m in enumerate(MISSIONS):
                            vac = {
                                "Fecha":fecha,"Rut":rut,
                                "Cod Objetivo": m.get("objetivo",""),
                                "Familia": FAMILIA_POR_MISION.get(m["nombre"],""),
                                "Especialidad": ESPECIALIDAD_POR_MISION.get(m["nombre"],""),
                                "Caso Encontrado":"Paciente Saltado","Objetivo":"N/A",
                                "Mensual":"Sin Día","Seguimiento":"Saltado",
                                "Fecha IPD":"", "Estado IPD":"", "Diagnóstico IPD":"", "Observación":"Paciente Saltado",
                            }
                            if m.get("habilitantes"): vac.update({"Hab?":"No","Habilitante":"","Fecha Hábil":"","Hab Vig?":"No"})
                            if m.get("usar_ng", True): vac.update({"NG?":"No","NG Fecha":"","NG Vig?":"No"})
                            filas_por_mision[i_m].append(vac)
                            for col in cols_mision(m):
                                if col in ("Fecha","Rut"): continue
                                base_conjunta[f"M{i_m+1} {col}"] = vac.get(col, "")
                        filas_conjuntas.append(base_conjunta)
                        break
                    else:
                        raise TimeoutException("No se pudo escribir el RUT")

                def click_buscar():
                    ok = sigges._click(["/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/button"],
                                       scroll=False, wait_spinner=True, raise_on_spinner_timeout=True,
                                       spinner_timeout=spinner_timeout_actual)
                    if not ok: raise TimeoutException("Botón Buscar no clickeable")
                    sigges.esperar_spinner(disappear_timeout=spinner_timeout_actual, raise_on_timeout=True)
                    time.sleep(POST_BUSQUEDA_SLEEP); return True
                ok,_ = intentar_paso("Buscar paciente", click_buscar)
                if not ok:
                    if _=="SKIP":
                        base_conjunta = {"Fecha":fecha,"Rut":rut}
                        for i_m, m in enumerate(MISSIONS):
                            vac = {
                                "Fecha":fecha,"Rut":rut,
                                "Cod Objetivo": m.get("objetivo",""),
                                "Familia": FAMILIA_POR_MISION.get(m["nombre"],""),
                                "Especialidad": ESPECIALIDAD_POR_MISION.get(m["nombre"],""),
                                "Caso Encontrado":"Paciente Saltado","Objetivo":"N/A",
                                "Mensual":"Sin Día","Seguimiento":"Saltado",
                                "Fecha IPD":"", "Estado IPD":"", "Diagnóstico IPD":"", "Observación":"Paciente Saltado",
                            }
                            if m.get("habilitantes"): vac.update({"Hab?":"No","Habilitante":"","Fecha Hábil":"","Hab Vig?":"No"})
                            if m.get("usar_ng", True): vac.update({"NG?":"No","NG Fecha":"","NG Vig?":"No"})
                            filas_por_mision[i_m].append(vac)
                            for col in cols_mision(m):
                                if col in ("Fecha","Rut"): continue
                                base_conjunta[f"M{i_m+1} {col}"] = vac.get(col, "")
                        filas_conjuntas.append(base_conjunta)
                        break
                    else:
                        raise TimeoutException("Fallo al buscar paciente")

                # 2) Mini-tabla robusta
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
                    # Sin caso (no es error)
                    base_conjunta = {"Fecha":fecha,"Rut":rut}
                    for i_m, m in enumerate(MISSIONS):
                        vac = {
                            "Fecha":fecha,"Rut":rut,
                            "Cod Objetivo": m.get("objetivo",""),
                            "Familia": FAMILIA_POR_MISION.get(m["nombre"],""),
                            "Especialidad": ESPECIALIDAD_POR_MISION.get(m["nombre"],""),
                            "Caso Encontrado":"Sin caso","Objetivo":"N/A",
                            "Mensual":"Sin Día","Seguimiento":"Sin Caso",
                            "Fecha IPD":"", "Estado IPD":"", "Diagnóstico IPD":"", "Observación":"Sin caso relevante en mini-tabla",
                        }
                        if m.get("habilitantes"): vac.update({"Hab?":"No","Habilitante":"","Fecha Hábil":"","Hab Vig?":"No"})
                        if m.get("usar_ng", True): vac.update({"NG?":"No","NG Fecha":"","NG Vig?":"No"})
                        filas_por_mision[i_m].append(vac)
                        for col in cols_mision(m):
                            if col in ("Fecha","Rut"): continue
                            base_conjunta[f"M{i_m+1} {col}"] = vac.get(col, "")
                    filas_conjuntas.append(base_conjunta)
                    log(INFO, "  → Sin caso relevante en mini-tabla. Se omite Cartola.")
                    break

                # 3) Cartola
                def abrir_cartola():
                    if not sigges.ir_a_cartola(spinner_timeout=spinner_timeout_actual, raise_on_spinner_timeout=True):
                        raise TimeoutException("No se pudo abrir la Cartola Unificada")
                    sigges.esperar_spinner(disappear_timeout=spinner_timeout_actual, raise_on_timeout=True)
                    time.sleep(SLEEP_LECTURA_TABLAS)
                    sigges.activar_hitos_ges()
                    return True
                ok,_ = intentar_paso("Abrir Cartola", abrir_cartola)
                if not ok:
                    if _=="SKIP":
                        base_conjunta = {"Fecha":fecha,"Rut":rut}
                        for i_m, m in enumerate(MISSIONS):
                            vac = {
                                "Fecha":fecha,"Rut":rut,
                                "Cod Objetivo": m.get("objetivo",""),
                                "Familia": FAMILIA_POR_MISION.get(m["nombre"],""),
                                "Especialidad": ESPECIALIDAD_POR_MISION.get(m["nombre"],""),
                                "Caso Encontrado":"Paciente Saltado","Objetivo":"N/A",
                                "Mensual":"Sin Día","Seguimiento":"Saltado",
                                "Fecha IPD":"", "Estado IPD":"", "Diagnóstico IPD":"", "Observación":"Paciente Saltado",
                            }
                            if m.get("habilitantes"): vac.update({"Hab?":"No","Habilitante":"","Fecha Hábil":"","Hab Vig?":"No"})
                            if m.get("usar_ng", True): vac.update({"NG?":"No","NG Fecha":"","NG Vig?":"No"})
                            filas_por_mision[i_m].append(vac)
                            for col in cols_mision(m):
                                if col in ("Fecha","Rut"): continue
                                base_conjunta[f"M{i_m+1} {col}"] = vac.get(col, "")
                        filas_conjuntas.append(base_conjunta)
                        break
                    else:
                        raise TimeoutException("Fallo abriendo cartola")

                # Fallecimiento (para logs y observación)
                fall_dt = sigges.leer_fallecimiento()
                log(WARN if fall_dt else INFO, f"{'Fallecido: ' + fall_dt.strftime('%d/%m/%Y') if fall_dt else 'Paciente Vivo'}")

                # NG global (quimio) — solo si alguna misión usa NG
                if any(m.get("usar_ng", True) for m in MISSIONS):
                    ng_global, ng_txt, ng_dt = scan_no_ges(sigges.driver, fobj)
                    if ng_global: log(DATA, f"Quimio NG detectada: {ng_txt}")
                else:
                    ng_global, ng_txt, ng_dt = (False, None, None)

                time.sleep(SLEEP_LECTURA_TABLAS)
                casos = sigges.lista_de_casos_cartola()

                resultados_paciente: Dict[int, Dict[str,Any]] = {}
                for i_m, m in enumerate(MISSIONS):
                    r = analizar_mision(sigges, m, casos, fobj, fecha, fall_dt, ng_global, ng_txt, ng_dt)
                    r.update({"Fecha":fecha,"Rut":rut})
                    resultados_paciente[i_m]=r

                for i_m in range(len(MISSIONS)):
                    filas_por_mision[i_m].append(resultados_paciente[i_m])

                # Si alguna vez activas "Detallado", respeta orden base con prefijos
                base={"Fecha":fecha,"Rut":rut}
                for i_m,m in enumerate(MISSIONS):
                    r=resultados_paciente[i_m]
                    for col in cols_mision(m):
                        if col in ("Fecha","Rut"): continue
                        base[f"M{i_m+1} {col}"]=r.get(col,"")
                filas_conjuntas.append(base)

                break  # paciente OK

            except SpinnerStuck as e:
                intentos_graves += 1
                log(WARN, f"Spinner pegado: {e}")
                if intentos_graves > MAX_REINTENTOS_GRAVES_POR_PACIENTE:
                    log(WARN, f"Demasiados intentos para {nombre}. Saltando.")
                    break
                time.sleep(ESPERA_ENTRE_INTENTOS_SEG)
                spinner_timeout_actual = min(spinner_timeout_actual * 2, SPINNER_DISAPPEAR_TIMEOUT_LARGO)

            except (TimeoutException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException) as e:
                intentos_graves += 1
                log(WARN, f"Error recuperable: {type(e).__name__}: {str(e)[:150]}")
                if intentos_graves > MAX_REINTENTOS_GRAVES_POR_PACIENTE:
                    log(WARN, f"Demasiados intentos para {nombre}. Saltando.")
                    break
                time.sleep(ESPERA_ENTRE_INTENTOS_SEG)

            except KeyboardInterrupt:
                log(ERR, "Interrumpido manualmente (Ctrl+C)."); driver.quit(); return

            except Exception as e:
                intentos_graves += 1
                log(WARN, f"Error inesperado: {type(e).__name__}: {str(e)[:150]}")
                if intentos_graves > MAX_REINTENTOS_GRAVES_POR_PACIENTE:
                    log(WARN, f"Demasiados intentos para {nombre}. Saltando.")
                    break
                time.sleep(ESPERA_ENTRE_INTENTOS_SEG)

    # Export
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
                    cols=["Fecha","Rut"]
                    for i_m,m in enumerate(MISSIONS): cols += cols_prefijo(i_m,m)
                    pd.DataFrame(filas_conjuntas, columns=cols).to_excel(w, index=False, sheet_name="Detallado")
                # Molde “Carga Masiva”
                pd.DataFrame([], columns=["FECHA","RUT","DV","PRESTACIONES","TIPO","PS-FAM","ESPECIALIDAD"]).to_excel(w, index=False, sheet_name="Carga Masiva")
            print(f"Archivo generado: {out}")
        except Exception as e:
            print(f"Error generando archivo de salida: {e}")

    driver.quit()

if __name__=="__main__":
    ejecutar_revision()
