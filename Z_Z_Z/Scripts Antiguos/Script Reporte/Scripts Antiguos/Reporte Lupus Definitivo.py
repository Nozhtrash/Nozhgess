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
# PANEL DE CONTROL (Lupus con motor Reumatología + columnas de habilitantes)
# ═════════════════════════════════════════════════════════════════════════════

NOMBRE_DE_LA_MISION = "Lupus"
RUTA_ARCHIVO_ENTRADA = r"C:\Users\usuarioHGF\OneDrive\Documentos\WORK\Trabajo\Lupus.xlsx"
RUTA_CARPETA_SALIDA  = r"C:\Users\usuarioHGF\OneDrive\Documentos\WORK\Trabajo\Revisiones"
DIRECCION_DEBUG_EDGE = "localhost:9222"
EDGE_DRIVER_PATH     = r"C:\\Windows\\System32\\msedgedriver.exe"

# Excel (0-based)
AUTO_DETECTAR_COLUMNAS = True
INDICE_COLUMNA_FECHA  = 5   # F (si no hay encabezados)
INDICE_COLUMNA_RUT    = 1   # B
INDICE_COLUMNA_NOMBRE = 3   # D (solo logging)

# Reintentos / timing
MAXIMOS_REINTENTOS_POR_PACIENTE = 3
REINTENTOS_PASO = 3
ESPERA_ENTRE_INTENTOS_SEG = 5
ESPERA_REINTENTOS_PASO = 3
SLEEP_LECTURA_TABLAS = 1
VENTANA_VIGENCIA_DIAS = 90

# Spinner / tiempos
SPINNER_APPEAR_TIMEOUT = 1.5
SPINNER_DISAPPEAR_TIMEOUT = 25
SPINNER_DISAPPEAR_TIMEOUT_LARGO = 120
SPINNER_SETTLE = 0.5
POST_BUSQUEDA_SLEEP = 1

# Mini-tabla
MINI_TABLA_REINTENTOS = 3
MINI_TABLA_SLEEP = 1
MINI_TABLA_STABLE_READS = 2

# Exportación
HOJA_POR_MISION = True

# Consola / logging
MINI_TABLA_MODO = "compacto"  # "oculto" | "compacto" | "detallado"
OMITIR_EVENTO_SIN_CASO = True   # ← ojo: nombre correcto (arregla el error de Pylance)
DEBUG_PRINT_CODES = False

# Interacción
MODO_INTERACTIVO_ERRORES = True
MAX_REINTENTOS_GRAVES_POR_PACIENTE = 3
GC_CADA_N_PACIENTES = 60

TOP_K_HABILITANTES = 1  # para Lupus usamos el último habilitante principal

# ——— Toggle IPD ———
REVISAR_IPD = True

# Familia/Especialidad de Lupus
FAMILIA_POR_MISION = {
    "Lupus": "78",
}
ESPECIALIDAD_POR_MISION = {
    "Lupus": "13-13-01",
}

# Misiones (estructura Reuma + habilitantes visibles)
MISSIONS: List[Dict[str, Any]] = [
    {
        "nombre": "Lupus",
        "keywords": ["lupus"],
        "objetivo": "0101113",  # control lupus
        "usar_habilitantes": True,
        # fármacos/infusiones que habilitan (ejemplos usados en tus versiones previas)
        "habilitantes": ["3901101", "3901102", "3901201", "3901202"],
        "require_any": True,
        "top_k": TOP_K_HABILITANTES,
        "usar_ng": False,
    },
]

# ═════════════════════════════════════════════════════════════════════════════
# XPATHs BASE (mismo set robusto de Reumatología)
# ═════════════════════════════════════════════════════════════════════════════
XP_CONT_CARTOLA   = "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]"
XP_RUT_INPUT      = "/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/div/div/input"
XP_BTN_BUSCAR     = "/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/button"
XP_MENU_BUSCAR    = "/html/body/div/main/div[2]/nav/div[1]/div[2]/a[1]"
XP_MENU_CARTOLA   = "/html/body/div/main/div[2]/nav/div[1]/div[2]/a[4]"
XP_CHK_HITOS_GES  = "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div/div/label/input"

# Fallback absolutos para IPD (dos ubicaciones vistas)
IPD_TBODY_CANDIDATE_ABS = [
    "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[2]/div[4]/div[2]/div/table/tbody",
    "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[7]/div[4]/div[2]/div/table/tbody",
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
# NO GES (hook futuro)
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
# SELENIUM WRAPPER (con IPD robusto)
# ═════════════════════════════════════════════════════════════════════════════
class SiggesDriver:
    def __init__(self, driver: webdriver.Remote) -> None:
        self.driver = driver

    # ---------- Infra ----------
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

    # ---------- Navegación ----------
    def asegurar_en_busqueda(self) -> None:
        try:
            if "actualizaciones" in self.driver.current_url:
                self.driver.get("https://www.sigges.cl/#/busqueda-de-paciente")
                self.esperar_spinner(raise_on_timeout=False)
        except:
            pass
        if self._find([XP_RUT_INPUT],"presence",2):
            return
        self._click([XP_MENU_BUSCAR], scroll=False, wait_spinner=True)

    def ir_a_cartola(self, spinner_timeout=SPINNER_DISAPPEAR_TIMEOUT, raise_on_spinner_timeout=True) -> bool:
        return self._click(
            [XP_MENU_CARTOLA],
            scroll=False, wait_spinner=True,
            raise_on_spinner_timeout=raise_on_spinner_timeout,
            spinner_timeout=spinner_timeout
        )

    def activar_hitos_ges(self) -> None:
        chk = self._find([XP_CHK_HITOS_GES], "presence", 20)
        if not chk: return
        try:
            if not chk.is_selected():
                self._click([XP_CHK_HITOS_GES], True, True)
        except: pass
        root = self._find([XP_CONT_CARTOLA], "presence", 5)
        end = time.time()+2
        while time.time()<end:
            try:
                if root and root.find_elements(By.CSS_SELECTOR,"div.contRow"): return
            except: pass
            time.sleep(0.25)

    def lista_de_casos_cartola(self) -> List[str]:
        time.sleep(SLEEP_LECTURA_TABLAS)
        root = self._find([XP_CONT_CARTOLA], "presence", 5)
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

    # ---------- por-caso ----------
    def _case_root(self, i:int) -> Optional[Any]:
        n=i+1
        try:
            return self._find([f"({XP_CONT_CARTOLA})/div[{n}]"], "presence", 8)
        except:
            return None

    def expandir_caso(self, i:int) -> Optional[Any]:
        root = self._case_root(i)
        if not root: return None
        try:
            if not root.find_elements(By.XPATH, ".//table"):
                self._click([f"({XP_CONT_CARTOLA})/div[{i+1}]/div/label/input", f"({XP_CONT_CARTOLA})/div[{i+1}]"], wait_spinner=False)
                time.sleep(0.25)
        except: pass
        return root

    def cerrar_caso_por_indice(self, i:int)->None:
        n=i+1
        try:
            self._click([f"({XP_CONT_CARTOLA})/div[{n}]/div/label/input", f"({XP_CONT_CARTOLA})/div[{n}]"], wait_spinner=False)
            time.sleep(0.3)
        except: pass

    def _prestaciones_tbody(self, i:int) -> Optional[Any]:
        n=i+1; base = XP_CONT_CARTOLA
        xps = [
            f"({base})/div[{n}]/div[6]/div[2]/div/table/tbody",
            f"({base})/div[{n}]//table/tbody"
        ]
        for xp in xps:
            try:
                return WebDriverWait(self.driver, 8).until(EC.presence_of_element_located((By.XPATH, xp)))
            except: continue
        return None

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

    # ---------- IPD ROBUSTO ----------
    def _find_section_label_p(self, root, needle: str) -> Optional[Any]:
        try:
            nd = _norm(needle)
            for el in root.find_elements(By.XPATH, ".//div/label/p"):
                if _norm(el.text) and nd.split("(")[0].strip() in _norm(el.text):
                    return el
        except: pass
        return None

    def _tbody_from_label_p(self, p_el) -> Optional[Any]:
        xps = [
            "../../../following-sibling::div[1]//table/tbody",
            "../../following-sibling::div[1]//table/tbody",
            "../following-sibling::div[1]//table/tbody",
            "ancestor::div[1]/following-sibling::div[1]//table/tbody",
            "ancestor::div[2]/following-sibling::div[1]//table/tbody",
            "ancestor::div[3]/following-sibling::div[1]//table/tbody",
        ]
        for xp in xps:
            try:
                tb = p_el.find_element(By.XPATH, xp)
                if tb: return tb
            except: continue
        return None

    def _thead_from_tbody(self, tbody) -> Optional[Any]:
        try:
            return tbody.find_element(By.XPATH, "../thead")
        except Exception:
            try:
                return tbody.find_element(By.XPATH, "ancestor::table/thead")
            except Exception:
                return None

    def _map_indices_thead(self, thead_el) -> dict:
        mapping = {}
        try:
            ths = thead_el.find_elements(By.TAG_NAME, "th")
            for i, th in enumerate(ths):
                lab = _norm(th.text or "")
                if lab: mapping[lab] = i
        except: pass
        return mapping

    def _thead_has_ipd(self, thead) -> bool:
        try:
            mp = self._map_indices_thead(thead)
            has_diag = any("diagnostico" in k for k in mp.keys())
            has_conf = any("confirma" in k or "descart" in k or "confirm" in k for k in mp.keys())
            return has_diag and has_conf
        except:
            return False

    def leer_ipd(self, i:int) -> Tuple[str, str, str]:
        """Retorna (fecha_ipd, estado_ipd, diagnostico_ipd). Cierra el caso al terminar."""
        fecha_ipd = estado_ipd = diag_ipd = ""
        try:
            root = self.expandir_caso(i)
            if not root:
                return "", "", ""
            p = self._find_section_label_p(root, "informes de proceso de diagnóstico")
            thead, tbody = None, None
            if p:
                try:
                    txt = (p.text or "").strip()
                    m = re.search(r"\((\d+)\)", txt)
                    if m and int(m.group(1)) == 0:
                        return "", "", ""
                except: pass
                tbody = self._tbody_from_label_p(p); thead = self._thead_from_tbody(tbody) if tbody else None

            if not tbody:
                for xp in IPD_TBODY_CANDIDATE_ABS:
                    tb = self._find([xp], "presence", 2)
                    if tb:
                        th = self._thead_from_tbody(tb)
                        if th and self._thead_has_ipd(th):
                            tbody, thead = tb, th
                            break

            if not tbody:
                return "", "", ""

            # Mapear índices
            idx_fecha = 2; idx_estado = 6; idx_diag = 7
            if thead:
                try:
                    mp = self._map_indices_thead(thead)
                    for k,v in mp.items():
                        if "fecha ipd" in k or ("fecha" in k and v != 0): idx_fecha = v
                    for k,v in mp.items():
                        if "confirma" in k or "descart" in k or "confirm" in k: idx_estado = v
                    for k,v in mp.items():
                        if "diagnostico" in k: idx_diag = v
                except: pass

            # Elegir la fila más reciente
            best = {"f": None, "fecha":"", "estado":"", "diag":""}
            rows = tbody.find_elements(By.TAG_NAME, "tr") or []
            for r in rows:
                try:
                    tds = r.find_elements(By.TAG_NAME, "td")
                    f_txt = (tds[idx_fecha].text or "").strip() if len(tds)>idx_fecha else ""
                    e_txt = (tds[idx_estado].text or "").strip() if len(tds)>idx_estado else ""
                    d_txt = (tds[idx_diag].text or "").replace("\n"," ").strip() if len(tds)>idx_diag else ""
                    if not f_txt:
                        m = _ddmmyyyy.search(r.text or "")
                        if m: f_txt = m.group(1)
                    f_dt = dparse(f_txt)
                    if best["f"] is None or (f_dt and best["f"] and f_dt>best["f"]) or (f_dt and best["f"] is None):
                        best = {"f": f_dt, "fecha":f_txt, "estado":e_txt, "diag":d_txt}
                except: continue

            fecha_ipd = best["fecha"] or ""
            estado_ipd = best["estado"] or ""
            diag_ipd = best["diag"] or ""
        finally:
            try: self.cerrar_caso_por_indice(i)
            except: pass
        return fecha_ipd, estado_ipd, diag_ipd

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
                    out = [r for r in out if "evento sin caso" not in _norm(r["problema"]) ]
                return out
        else:
            stable = 0
            last_key = key
            last_snap = snap

        time.sleep(0.25)

    out = last_snap
    if OMITIR_EVENTO_SIN_CASO:
        out = [r for r in out if "evento sin caso" not in _norm(r["problema"]) ]
    return out

# ═════════════════════════════════════════════════════════════════════════════
# LÓGICA DE MISIÓN (con columnas Habilitantes visibles)
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

def clasificar_seguimiento(obj_dt: Optional[datetime], hab_dt: Optional[datetime],
                           ng_dt: Optional[datetime], fobj: datetime) -> str:
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


def filtrar_por_ano(prest: List[Dict[str,str]], ano: int) -> List[Dict[str,str]]:
    out=[]
    for p in prest:
        f = dparse(p.get("fecha",""))
        if f and f.year == ano:
            out.append({**p, "dt": f})
    return out


def contar_objetivo_en_ano(prest_ano: List[Dict[str,str]], objetivo: str) -> int:
    return sum(1 for p in prest_ano if p.get("codigo")==objetivo)


def observacion_frecuencia(cnt: int, max_anual: int, ano: int, objetivo: str) -> Optional[str]:
    if cnt > max_anual:
        return f"Excede frecuencia {cnt}/{max_anual} en {ano} (cód. {objetivo})"
    return None


def resumen_ipd_corto(estado_ipd: str) -> Optional[str]:
    if not estado_ipd: return None
    e = _norm(estado_ipd)
    if "confirma" in e or "confirm" in e: return "IPD: Confirma"
    if "descarta" in e: return "IPD: Descarta"
    return f"IPD: {estado_ipd.strip()}"


def analizar_mision(sigges: SiggesDriver, m: Dict[str,Any], casos: List[str], fobj: datetime,
                    fexcel: str, fall_dt: Optional[datetime],
                    ng_global: bool, ng_txt: Optional[str], ng_dt: Optional[datetime]) -> Dict[str,Any]:

    nombre_m = m["nombre"]
    objetivo = m.get("objetivo","")
    usar_habs = m.get("usar_habilitantes", False)
    habs = m.get("habilitantes", []) if usar_habs else []

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
        "Fecha IPD":"", "Estado IPD":"", "Diagnóstico IPD":"",
        "Observación":""
    }

    # Columnas visibles de habilitantes (si aplica)
    if usar_habs and habs:
        res.update({"Hab?":"No","Habilitante":"","Fecha Hábil":"","Hab Vig?":"No"})

    idx, texto, _ = elegir_caso_mas_reciente(casos, m["keywords"])
    if idx is None:
        res["Observación"] = "Sin caso relevante en mini-tabla"
        return res

    res["Caso Encontrado"] = texto or "Caso relevante"

    # 1) IPD primero (si corresponde)
    fipd = eipd = dipd = ""
    if REVISAR_IPD:
        fipd, eipd, dipd = sigges.leer_ipd(idx)
        res["Fecha IPD"] = fipd or ""
        res["Estado IPD"] = eipd or ""
        res["Diagnóstico IPD"] = (dipd or "").strip()

    # 2) Reabrir y leer Prestaciones Otorgadas
    sigges.expandir_caso(idx)
    tb = sigges._prestaciones_tbody(idx)
    prestaciones = sigges.leer_prestaciones_desde_tbody(tb) if tb is not None else []
    sigges.cerrar_caso_por_indice(idx)

    if DEBUG_PRINT_CODES and prestaciones:
        try: log(CODE, "    DEBUG Códigos ⟶ " + ", ".join(f"{p['codigo']}@{p['fecha']}" for p in prestaciones))
        except: pass

    # Calendario (objetivo y mensualidad dentro del año de la fecha Excel)
    ano = fobj.year if fobj else None
    prest_del_ano = filtrar_por_ano(prestaciones, ano) if ano else []

    obj_dates = [p["dt"] for p in prest_del_ano if p.get("codigo")==objetivo]
    last_obj = max(obj_dates) if obj_dates else None
    if last_obj: res["Objetivo"]=last_obj.strftime("%d/%m/%Y")
    res["Mensual"] = mensual_categoria([f for f in obj_dates if same_month(f, fobj)], fobj) if obj_dates else "Sin Día"

    # Habilitantes
    last_hab = None
    last_hab_code = None
    if usar_habs and habs:
        lst = listar_habilitantes(prestaciones, habs, fobj)
        if lst:
            top = lst[: m.get("top_k", TOP_K_HABILITANTES)]
            res["Hab?"] = "Sí"
            res["Habilitante"] = " | ".join(c for c,_ in top)
            res["Fecha Hábil"] = " | ".join(d.strftime("%d/%m/%Y") for _,d in top)
            last_hab_code, last_hab = lst[0]  # (codigo, fecha)
            res["Hab Vig?"] = "Sí" if en_vig(fobj,last_hab) else "No"
        else:
            res["Hab?"] = "No"; res["Habilitante"] = ""; res["Fecha Hábil"] = ""; res["Hab Vig?"] = "No"

    # Observación (concisa)
    obs_tags: List[str] = []
    if REVISAR_IPD and not (fipd or eipd or dipd):
        obs_tags.append("Sin IPD")
    if last_hab:
        obs_tags.append(f"Hábil {'vigente' if en_vig(fobj,last_hab) else 'antigua'} {last_hab.strftime('%d/%m/%Y')} ({last_hab_code})")
    res["Observación"] = join_tags(obs_tags) if obs_tags else ""

    # Seguimiento (considera habilitante)
    seg_tags = [clasificar_seguimiento(last_obj, last_hab, None, fobj)]
    ipd_tag = resumen_ipd_corto(eipd) if REVISAR_IPD else None
    if ipd_tag: seg_tags.append(ipd_tag)
    if not last_obj: seg_tags.append("Sin Objetivo")
    res["Seguimiento"] = join_tags(seg_tags)

    try:
        log(INFO, f"[{m['nombre']}] Caso: {res['Caso Encontrado']}")
        if res["Fecha IPD"] or res["Estado IPD"] or res["Diagnóstico IPD"]:
            log(DATA, f"    IPD ⟶ {res['Fecha IPD']} | {res['Estado IPD']} | {res['Diagnóstico IPD'][:60]}")
        if usar_habs and res.get("Hab?")=="Sí":
            log(CODE, f"    Habilitante ⟶ {res.get('Habilitante')} @ {res.get('Fecha Hábil')}")
        log(OK if res["Objetivo"]!='N/A' else WARN, f"    Seguimiento ⟶ {res['Seguimiento']}")
        if res["Observación"]:
            log(WARN, f"    Obs ⟶ {res['Observación']}")
    except: pass

    return res

# ═════════════════════════════════════════════════════════════════════════════
# EXPORTACIÓN (ORDEN REUMATOLOGÍA + columnas Habilitantes visibles)
# ═════════════════════════════════════════════════════════════════════════════

def cols_mision(m: Dict[str,Any]) -> List[str]:
    cols = [
        "Fecha","Rut","Cod Objetivo","Familia","Especialidad",
        "Caso Encontrado","Objetivo","Mensual","Seguimiento",
        "Fecha IPD","Estado IPD","Diagnóstico IPD","Observación"
    ]
    if m.get("usar_habilitantes", False) and m.get("habilitantes"):
        cols = [
            "Fecha","Rut","Cod Objetivo","Familia","Especialidad",
            "Caso Encontrado","Objetivo","Mensual","Seguimiento",
            "Hab?","Habilitante","Fecha Hábil","Hab Vig?",
            "Fecha IPD","Estado IPD","Diagnóstico IPD","Observación"
        ]
    return cols


def cols_prefijo(i:int, m:Dict[str,Any])->List[str]:
    base=[
        "Cod Objetivo","Familia","Especialidad","Caso Encontrado","Objetivo","Mensual",
        "Seguimiento",
    ]
    if m.get("usar_habilitantes", False) and m.get("habilitantes"):
        base += ["Hab?","Habilitante","Fecha Hábil","Hab Vig?"]
    base += ["Fecha IPD","Estado IPD","Diagnóstico IPD","Observación"]
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
# AUTODETECCIÓN DE COLUMNAS (opcional)
# ═════════════════════════════════════════════════════════════════════════════

def detectar_indices_por_header(df: pd.DataFrame) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    cols = [str(c).strip().lower() for c in df.columns]
    def find(keys):
        for k in keys:
            for i,c in enumerate(cols):
                if k in c: return i
        return None
    return (
        find(["fecha despach", "fecha despacho", "fecha atención", "fecha atencion", "fecha"]),
        find(["rut"]),
        find(["nombre"]),
    )

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

    # Autodetectar columnas si procede
    global INDICE_COLUMNA_FECHA, INDICE_COLUMNA_RUT, INDICE_COLUMNA_NOMBRE
    if AUTO_DETECTAR_COLUMNAS:
        a,b,c = detectar_indices_por_header(df)
        INDICE_COLUMNA_FECHA  = a if a is not None else INDICE_COLUMNA_FECHA
        INDICE_COLUMNA_RUT    = b if b is not None else INDICE_COLUMNA_RUT
        INDICE_COLUMNA_NOMBRE = c if c is not None else INDICE_COLUMNA_NOMBRE
        try:
            log(INFO, f"Mapeo columnas → FECHA='{df.columns[INDICE_COLUMNA_FECHA]}' | RUT='{df.columns[INDICE_COLUMNA_RUT]}' | NOMBRE='{df.columns[INDICE_COLUMNA_NOMBRE]}'")
        except: pass

    filas_por_mision: Dict[int,List[Dict[str,Any]]] = {i:[] for i in range(len(MISSIONS))}
    filas_conjuntas: List[Dict[str,Any]] = []
    total=len(df)

    def agregar_filas_vacias(fecha: str, rut: str, motivo: str):
        base_conjunta = {"Fecha":fecha,"Rut":rut}
        for i_m, m in enumerate(MISSIONS):
            vac = {
                "Fecha":fecha,"Rut":rut,
                "Cod Objetivo": m.get("objetivo",""),
                "Familia": FAMILIA_POR_MISION.get(m["nombre"],""),
                "Especialidad": ESPECIALIDAD_POR_MISION.get(m["nombre"],""),
                "Caso Encontrado":"Sin caso","Objetivo":"N/A",
                "Mensual":"Sin Día","Seguimiento":"Sin Caso",
                "Fecha IPD":"", "Estado IPD":"", "Diagnóstico IPD":"",
                "Observación": motivo,
            }
            if m.get("usar_habilitantes", False) and m.get("habilitantes"):
                vac.update({"Hab?":"No","Habilitante":"","Fecha Hábil":"","Hab Vig?":"No"})
            filas_por_mision[i_m].append(vac)
            if not HOJA_POR_MISION:
                for col in cols_mision(m):
                    if col in ("Fecha","Rut"): continue
                    base_conjunta[f"M{i_m+1} {col}"] = vac.get(col, "")
        if not HOJA_POR_MISION:
            filas_conjuntas.append(base_conjunta)

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
                # Ir a Búsqueda
                ok, _ = intentar_paso("Ir a búsqueda", lambda: (sigges.asegurar_en_busqueda() or True))
                if not ok:
                    if _ == "SKIP":
                        agregar_filas_vacias(fecha, rut, "Paciente Saltado"); break
                    else:
                        raise TimeoutException("No se pudo ir a búsqueda")

                # Escribir RUT
                def obtener_input():
                    el = sigges._find([XP_RUT_INPUT], "presence", 20)
                    if not el: raise TimeoutException("Campo RUT no encontrado")
                    try: el.clear()
                    except StaleElementReferenceException:
                        el = sigges._find([XP_RUT_INPUT], "presence", 10); el.clear()
                    el.send_keys(rut); return True
                ok, res = intentar_paso("Escribir RUT", obtener_input)
                if not ok:
                    if res=="SKIP":
                        agregar_filas_vacias(fecha, rut, "Paciente Saltado"); break
                    else:
                        raise TimeoutException("No se pudo escribir el RUT")

                # Buscar
                def click_buscar():
                    ok = sigges._click([XP_BTN_BUSCAR], scroll=False, wait_spinner=True, raise_on_spinner_timeout=True,
                                       spinner_timeout=spinner_timeout_actual)
                    if not ok: raise TimeoutException("Botón Buscar no clickeable")
                    sigges.esperar_spinner(disappear_timeout=spinner_timeout_actual, raise_on_timeout=True)
                    time.sleep(POST_BUSQUEDA_SLEEP); return True
                ok,_ = intentar_paso("Buscar paciente", click_buscar)
                if not ok:
                    if _=="SKIP":
                        agregar_filas_vacias(fecha, rut, "Paciente Saltado"); break
                    else:
                        raise TimeoutException("Fallo al buscar paciente")

                # Mini-tabla
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
                    filas = mini if MINI_TABLA_MODO=="detallado" else [r for r in mini if es_relevante(r)];
                    for i2, r2 in enumerate(filas,1):
                        marca = " ✔" if es_relevante(r2) else ""
                        linea = f"  • {i2}. {r2['problema']} | {r2.get('estado') or '—'}{marca}"
                        log(OK if marca else WARN, linea)

                if not tiene_relevante:
                    agregar_filas_vacias(fecha, rut, "Sin caso relevante en mini-tabla")
                    log(INFO, "  → Sin caso relevante en mini-tabla. Se omite Cartola.")
                    break

                # Cartola
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
                        agregar_filas_vacias(fecha, rut, "Paciente Saltado"); break
                    else:
                        raise TimeoutException("Fallo abriendo cartola")

                # Fallecimiento
                fall_dt = sigges.leer_fallecimiento()
                log(WARN if fall_dt else INFO, f"{'Fallecido: ' + fall_dt.strftime('%d/%m/%Y') if fall_dt else 'Paciente Vivo'}")

                # NG global (no usado por defecto)
                if any(m.get("usar_ng", False) for m in MISSIONS):
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

                if not HOJA_POR_MISION:
                    base={"Fecha":fecha,"Rut":rut}
                    for i_m,m in enumerate(MISSIONS):
                        rr=resultados_paciente[i_m]
                        for col in cols_mision(m):
                            if col in ("Fecha","Rut"): continue
                            base[f"M{i_m+1} {col}"]=rr.get(col,"")
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
    if HOJA_POR_MISION and any(filas_por_mision.values()) or (not HOJA_POR_MISION and filas_conjuntas):
        os.makedirs(RUTA_CARPETA_SALIDA, exist_ok=True)
        ts=datetime.now().strftime("%Y%m%d_%H%M")
        out=os.path.join(RUTA_CARPETA_SALIDA, f"Revision_{NOMBRE_DE_LA_MISION}_{ts}.xlsx")
        try:
            with pd.ExcelWriter(out, engine="openpyxl") as w:
                if HOJA_POR_MISION:
                    for i_m,m in enumerate(MISSIONS):
                        df_out = pd.DataFrame(filas_por_mision[i_m], columns=cols_mision(m))
                        df_out.to_excel(w, index=False, sheet_name=f"Mision {i_m+1}")
                else:
                    cols=["Fecha","Rut"]
                    for i_m,m in enumerate(MISSIONS): cols += cols_prefijo(i_m,m)
                    pd.DataFrame(filas_conjuntas, columns=cols).to_excel(w, index=False, sheet_name="Detallado")

                # Hoja “Carga Masiva” vacía (molde fijo)
                pd.DataFrame([], columns=["FECHA","RUT","DV","PRESTACIONES","TIPO","PS-FAM","ESPECIALIDAD"]).to_excel(w, index=False, sheet_name="Carga Masiva")

            print(f"Archivo generado: {out}")
        except Exception as e:
            print(f"Error generando archivo de salida: {e}")

    driver.quit()

if __name__=="__main__":
    ejecutar_revision()
