# src/core/modules/data.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING
import re
import time
import traceback
from datetime import datetime
from selenium.webdriver.common.by import By

from src.utils.Direcciones import XPATHS
from src.utils.Terminal import log_error, log_info, log_warn
from src.core.Formatos import dparse, _norm

if TYPE_CHECKING:
    from src.core.state import DriverState
    from src.core.contracts import SiggesDriverProtocol

class DataParsingMixin:
    """
    Mixin DataParsing: Maneja lectura de tablas, cartola, y detalles de caso.
    Utiliza DriverState para consistencia.
    """
    
    # Type hints for specialized engines provided by CoreMixin
    state: DriverState
    log: LoggerPro
    waits: SmartWait
    selectors: SelectorEngine

    def activar_hitos_ges(self) -> None:
        """Activa el checkbox de 'Mostrar solo hitos GES'."""
        try:
            chk = self._find(XPATHS["CHK_HITOS_GES"], "presence", "cartola_click_hitos")
            if chk and not chk.is_selected():
                self._click(XPATHS["CHK_HITOS_GES"], True, True, "cartola_click_hitos")
        except Exception:
            pass

    # =========================================================================
    #                        LECTURAS BÁSICAS
    # =========================================================================

    def leer_edad(self) -> Optional[int]:
        """Lee la edad del paciente de forma OPTIMIZADA."""
        el = self._find(XPATHS["EDAD_PACIENTE"], "visible", "mini_read_age_fast")
        if not el:
            return None
        
        txt = (el.text or "").strip()
        if not txt:
            return None
        
        m = re.search(r'(\d+)\s*[Aa]ño', txt)
        if m:
            edad = int(m.group(1))
            return edad if 0 <= edad <= 130 else None
        
        m = re.search(r'(\d+)', txt)
        if m:
            edad = int(m.group(1))
            return edad if 0 <= edad <= 130 else None
        
        return None

    def leer_fallecimiento(self) -> Optional[Any]:
        """Lee la fecha de fallecimiento si existe."""
        try:
            xp = "//div[span[normalize-space(.)='Fecha de fallecimiento'] and p]"
            el = self._find([xp], "presence", "cartola_read_fallecimiento")
            if el:
                return dparse((el.find_element(By.TAG_NAME, "p").text or "").strip())
        except Exception:
            pass
        return None

    def lista_de_casos_cartola(self) -> List[str]:
        """Obtiene lista de nombres de casos de la cartola desde DIVs."""
        contenedor_xpaths = [
            "//div[contains(@class,'contRow') and contains(@class,'contRowBox') and contains(@class,'scrollH')]",
            "//div[@class='contRow contRowBox scrollH']",
            XPATHS["CONT_CARTOLA"],
        ]
        
        root = None
        for xpath in contenedor_xpaths:
            root = self._find([xpath] if isinstance(xpath, str) else xpath, "presence", "case_list_read")
            if root:
                break
        
        if not root:
            return []
        
        try:
            casos_divs = root.find_elements(By.XPATH, ".//div[@class='contRow'][.//input[@type='checkbox']]")
            casos_texto = []
            for div in casos_divs:
                try:
                    p_element = div.find_element(By.XPATH, ".//label/p")
                    texto = (p_element.text or "").strip()
                    if texto:
                        casos_texto.append(texto)
                except Exception:
                    continue
            return casos_texto
        except Exception:
            return []

    def _parsear_cartola_divs(self) -> List[Dict[str, Any]]:
        """Estrategia 1: Leer DIVs (Estructura Actual)"""
        datos_casos = []
        try:
            xpaths_cont = [
                "//div[contains(@class,'contRow') and contains(@class,'contRowBox') and contains(@class,'scrollH')]",
                "//div[@class='contRow contRowBox scrollH']",
                XPATHS["CONT_CARTOLA"]
            ]
            flat_xpaths = []
            for xp in xpaths_cont:
                if isinstance(xp, list): flat_xpaths.extend(xp)
                else: flat_xpaths.append(xp)
            
            root = None
            for xp in flat_xpaths:
                 root = self._find(xp, "presence", "case_list_read")
                 if root: break
            
            if not root:
                return []
                
            casos_divs = root.find_elements(By.XPATH, ".//div[@class='contRow'][.//input[@type='checkbox']]")
            
            for i, div in enumerate(casos_divs):
                try:
                    p = div.find_element(By.XPATH, ".//label/p")
                    raw_text = (p.text or "").strip()
                    if not raw_text: continue
                    
                    fecha_match = re.search(r'(\d{2}/\d{2}/\d{4})', raw_text)
                    nombre = raw_text
                    fecha_str = ""
                    estado = ""
                    cierre = "NO"
                    fecha_dt = datetime.min
                    
                    if fecha_match:
                        fecha_str = fecha_match.group(1)
                        parts = raw_text.split(fecha_str)
                        nombre_raw = parts[0].strip().rstrip(',').strip()
                        if "{" in nombre_raw:
                            nombre = nombre_raw.split('{')[0].replace('.', '').strip()
                        else:
                            nombre = nombre_raw.replace('.', '').strip()
                            
                        if len(parts) > 1:
                            rest = parts[1]
                            rest = re.sub(r'\d{2}:\d{2}:\d{2}', '', rest)
                            estado = rest.strip().lstrip(',').strip()
                            
                        try:
                            fecha_dt = datetime.strptime(fecha_str, "%d/%m/%Y")
                        except Exception:
                            pass
                    
                    if "cerrado" in estado.lower() or "cierre" in estado.lower():
                        cierre = "SI"
                        
                    datos_casos.append({
                        "caso": nombre,
                        "estado": estado,
                        "apertura": fecha_str,
                        "cierre": cierre,
                        "fecha_dt": fecha_dt,
                        "indice": i,
                        "raw_texto": raw_text
                    })
                except Exception:
                    continue
        except Exception as e:
            self.log.warn(f"Error parseando DIVs cartola: {e}")
        return datos_casos

    def _parsear_cartola_tabla(self) -> List[Dict[str, Any]]:
        """Estrategia 2: Leer TABLA (Fallback Legacy)"""
        datos_casos = []
        try:
            xpaths_tbody = [
                "//div[contains(@class,'contBox')]/div/div/table/tbody", 
                "/html/body/div/main/div[3]/div[2]/div[1]/div[3]/div/table/tbody"
            ]
            tbody = None
            for xp in xpaths_tbody:
                tbody = self._find(xp, "presence", "mini_find_table")
                if tbody: break
                
            if not tbody:
                return []

            filas = tbody.find_elements(By.TAG_NAME, "tr")
            for i, tr in enumerate(filas):
                try:
                    tds = tr.find_elements(By.TAG_NAME, "td")
                    if len(tds) < 6: continue
                    raw_nombre = tds[0].text.strip()
                    if "{" in raw_nombre:
                        nombre_limpio = raw_nombre.split('{')[0].replace('.', '').strip()
                    else:
                        nombre_limpio = raw_nombre.replace('.', '').strip()
                    
                    raw_apertura = tds[2].text.strip()
                    apertura = raw_apertura.split(' ')[0]
                    estado = tds[3].text.strip()
                    raw_cierre = tds[5].text.strip()
                    if not raw_cierre or raw_cierre.lower() in ["sin informacion", "sin información", "-", ""]:
                        cierre = "NO"
                    else:
                        cierre = raw_cierre.split(' ')[0]
                    
                    try:
                        dt_obj = datetime.strptime(apertura, "%d/%m/%Y")
                    except Exception:
                        dt_obj = datetime.min

                    datos_casos.append({
                        "caso": nombre_limpio,
                        "estado": estado,
                        "apertura": apertura,
                        "cierre": cierre,
                        "fecha_dt": dt_obj,
                        "indice": i, 
                        "raw_texto": raw_nombre
                    })
                except Exception:
                    continue
        except Exception:
            pass
        return datos_casos

    def extraer_tabla_provisoria_completa(self) -> List[Dict[str, Any]]:
        """Lee la lista de casos de la cartola (DIVs > Tabla)."""
        casos = self._parsear_cartola_divs()
        if casos: return casos
        return self._parsear_cartola_tabla()

    # =========================================================================
    #                      MANEJO DE CASOS
    # =========================================================================

    def _case_root(self, i: int) -> Optional[Any]:
        """Obtiene el div raíz de un caso por índice en la cartola."""
        try:
            contenedor_xpaths = [
                "//div[contains(@class,'contRow') and contains(@class,'contRowBox') and contains(@class,'scrollH')]",
                "//div[@class='contRow contRowBox scrollH']",
            ]
            contenedor = None
            for xpath in contenedor_xpaths:
                contenedor = self._find([xpath], "presence", "case_list_read")
                if contenedor: break
            
            if not contenedor: return None
            
            casos_divs = contenedor.find_elements(By.XPATH, ".//div[@class='contRow'][.//input[@type='checkbox']]")
            if 0 <= i < len(casos_divs):
                return casos_divs[i]
            return None
        except Exception:
            return None

    def expandir_caso(self, i: int) -> Optional[Any]:
        """Expande un caso haciendo click en su checkbox."""
        root = self._case_root(i)
        if not root: return None
        
        try:
            checkbox = root.find_element(By.XPATH, ".//input[@type='checkbox']")
            if not checkbox.is_selected():
                try:
                    checkbox.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", checkbox)
                
                # Esperar a que el estado cambie visualmente
                try:
                    WebDriverWait(self.driver, 1.0).until(lambda d: checkbox.is_selected())
                except TimeoutException:
                    pass
                
                self._wait_smart("spinner")
            return root
        except Exception:
            return None

    def cerrar_caso_por_indice(self, i: int) -> None:
        """Cierra un caso expandido haciendo click en su checkbox."""
        try:
            root = self._case_root(i)
            if root:
                checkbox = root.find_element(By.XPATH, ".//input[@type='checkbox']")
                if checkbox.is_selected():
                    try:
                        checkbox.click()
                    except Exception:
                        self.driver.execute_script("arguments[0].click();", checkbox)
                    
                    # Esperar a que se desmarque
                    try:
                        WebDriverWait(self.driver, 1.0).until(lambda d: not checkbox.is_selected())
                    except TimeoutException:
                        pass
        except Exception:
            pass

    # =========================================================================
    #                      PRESTACIONES
    # =========================================================================

    def _prestaciones_tbody(self, i: int) -> Optional[Any]:
        """Obtiene el tbody de prestaciones de un caso."""
        self.log.info(f"🔍 Buscando tbody de prestaciones para caso índice {i}")
        
        # Estrategia 1
        xpaths_estrategia_1 = [
            f"/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[{i + 2}]/div[6]/div[2]/div/table/tbody",
            f"/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[{i + 1}]/div[6]/div[2]/div/table/tbody",
            f"//div[@id='root']/main/div[3]/div[2]/div[1]/div[contains(@class,'')][position()=6 or position()=5]/div[1]/div[2]/div[{i + 2}]/div[6]/div[2]/div/table/tbody",
            f"//div[contains(@class,'contRow') and contains(@class,'scrollH')]/div[{i + 2}]/div[6]/div[2]/div/table/tbody",
            f"//div[contains(@class,'contRow') and contains(@class,'scrollH')]/div[{i + 1}]/div[6]/div[2]/div/table/tbody",
            f"//div[contains(@class,'contRow') and contains(@class,'scrollH')]/div[{i + 2}]//table/tbody",
            f"//div[contains(@class,'contRow') and contains(@class,'scrollH')]/div[{i + 1}]//table/tbody"
        ]
        
        for idx, xp in enumerate(xpaths_estrategia_1, 1):
            try:
                result = self.driver.find_element(By.XPATH, xp)
                if result:
                    log_info(f"   ✅ Encontrado con estrategia 1, intento {idx}")
                    return result
            except Exception:
                if idx == len(xpaths_estrategia_1):
                    log_warn(f"   ⚠️ Todos los intentos de estrategia 1 fallaron")
                continue
        
        log_warn("   ⚠️ Estrategia 1 falló, probando con búsqueda por label...")
        
        # Estrategia 2
        for idx_offset in [2, 1]:
            try:
                caso_div = self.driver.find_element(
                    By.XPATH, 
                    f"//div[contains(@class,'contRow') and contains(@class,'scrollH')]/div[{i + idx_offset}]"
                )
                if caso_div:
                    log_info(f"   ✅ Encontrado div del caso {i} con offset +{idx_offset}")
                    try:
                        tbody = caso_div.find_element(By.XPATH, ".//div[6]/div[2]/div/table/tbody")
                        if tbody:
                            log_info("   ✅ Encontrado tbody dentro del div del caso")
                            return tbody
                    except Exception:
                        tbody = caso_div.find_element(By.XPATH, ".//table/tbody")
                        if tbody:
                            log_info("   ✅ Encontrado tbody (fallback) dentro del div del caso")
                            return tbody
            except Exception:
                continue
        log_warn(f"   ⚠️ Estrategia 2 falló para todos los offsets")
        
        # Estrategia 3
        try:
            log_info("   🔍 Estrategia 3: Buscando todas las tablas visibles...")
            all_tbodies = self.driver.find_elements(By.XPATH, "//table/tbody")
            log_info(f"   📋 Encontradas {len(all_tbodies)} tablas en total")
            
            for idx, tbody in enumerate(all_tbodies):
                try:
                    rows = tbody.find_elements(By.TAG_NAME, "tr")
                    if not rows: continue
                    first_row = rows[0]
                    cols = first_row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 12:
                        codigo_txt = cols[7].text.strip() if len(cols) > 7 else ""
                        if codigo_txt and codigo_txt.isdigit():
                            log_info(f"      ✅ Tabla {idx} parece ser prestaciones (código en col 8: {codigo_txt})")
                            return tbody
                except Exception:
                    continue
            log_warn("   ⚠️ No se encontró tabla de prestaciones con características esperadas")
        except Exception as e:
            log_error(f"   ❌ Estrategia 3 falló: {e}")
        
        log_error(f"   ❌ NO se pudo encontrar tbody de prestaciones para caso {i}")
        return None

    def leer_prestaciones_desde_tbody(self, tbody: Any) -> List[Dict[str, str]]:
        """Lee prestaciones desde un tbody."""
        out = []
        if not tbody:
            log_warn("⚠️ tbody es None, no se pueden leer prestaciones")
            return out
        
        _ddmmyyyy = re.compile(r"\b(\d{2}/\d{2}/\d{4})\b", re.I)
        
        try:
            all_rows = tbody.find_elements(By.TAG_NAME, "tr")
            log_info(f"📋 Leyendo tbody con {len(all_rows)} filas")
            
            filas_procesadas = 0
            filas_descartadas = 0
            
            for tr in reversed(all_rows):
                tds = tr.find_elements(By.TAG_NAME, "td")
                if len(tds) < 9:
                    filas_descartadas += 1
                    continue
                
                # Use helper for date parsing
                f = (tds[2].text.strip().split(" ")[0] if len(tds) > 2 else "")
                if not dparse(f):
                    for c in tds:
                        m = _ddmmyyyy.search(c.text or "")
                        if m:
                            f = m.group(1)
                            break
                
                codigo = (tds[7].text or "").strip()
                glosa = (tds[8].text or "").strip()
                ref = (tds[0].text or "").strip()
                
                out.append({
                    "fecha": f, "codigo": codigo, "glosa": glosa, "ref": ref
                })
                filas_procesadas += 1
                
            self.log.info(f"✅ Procesadas {filas_procesadas} prestaciones ({filas_descartadas} descartadas)")
        except Exception as e:
            self.log.warn(f"⚠️ Error al leer prestaciones: {e}")
            self.log.warn(f"   Traceback: {traceback.format_exc()[:200]}")
        return out

    # =========================================================================
    #                    HELPERS PARA SECCIONES
    # =========================================================================

    def _find_section_label_p(self, root, needle: str):
        """Busca un label de sección por texto normalizado."""
        nd = _norm(needle)
        try:
            for el in root.find_elements(By.XPATH, ".//div/label/p"):
                txt = _norm(el.text or "")
                if txt and nd.split("(")[0].strip() in txt:
                    return el
        except Exception:
            pass
        return None

    def _tbody_from_label_p(self, p_el):
        """Obtiene tbody relativo a un label encontrado."""
        for xp in [
            "../../../following-sibling::div[1]//table/tbody",
            "../../following-sibling::div[1]//table/tbody",
            "../following-sibling::div[1]//table/tbody",
            "ancestor::div[1]/following-sibling::div[1]//table/tbody"
        ]:
            try:
                tb = p_el.find_element(By.XPATH, xp)
                if tb: return tb
            except Exception:
                continue
        return None

    # =========================================================================
    #                           IPD, OA, APS, SIC
    # =========================================================================

    def leer_ipd_desde_caso(self, root: Any, n: int) -> Tuple[List[str], List[str], List[str]]:
        if not root: return [], [], []
        try:
            tbody = None
            p = self._find_section_label_p(root, "informes de proceso de diagnóstico")
            if p: tbody = self._tbody_from_label_p(p)
            if not tbody:
                for xp in XPATHS.get("IPD_TBODY_FALLBACK", []):
                    try:
                        relative = "." + xp.split("/main")[1] if "/main" in xp else xp
                        tbody = root.find_element(By.XPATH, relative)
                        if tbody: break
                    except Exception: continue
            if not tbody: return [], [], []

            rows = tbody.find_elements(By.TAG_NAME, "tr") or []
            parsed = []
            for r in rows:
                try:
                    tds = r.find_elements(By.TAG_NAME, "td")
                    if len(tds) < 8: continue
                    f_txt = (tds[2].text or "").strip()
                    e_txt = (tds[6].text or "").strip()
                    d_txt = (tds[7].text or "").strip()
                    f_dt = dparse(f_txt) or 0
                    parsed.append((f_dt, f_txt, e_txt, d_txt))
                except Exception: continue
            parsed.sort(key=lambda x: x[0] if x[0] else 0, reverse=True)
            if n and n > 0: parsed = parsed[:n]
            return ([p[1] for p in parsed], [p[2] for p in parsed], [p[3] for p in parsed])
        except Exception: return [], [], []

    def leer_oa_desde_caso(self, root: Any, n: int) -> Tuple[List[str], List[str], List[str], List[str], List[str]]:
        if not root: return [], [], [], [], []
        try:
            tbody = None
            p = self._find_section_label_p(root, "ordenes de atencion")
            if p: tbody = self._tbody_from_label_p(p)
            if not tbody:
                for xp in XPATHS.get("OA_TBODY_FALLBACK", []):
                    try:
                        relative = "." + xp.split("/main")[1] if "/main" in xp else xp
                        tbody = root.find_element(By.XPATH, relative)
                        if tbody: break
                    except Exception: continue
            if not tbody: return [], [], [], [], []

            rows = tbody.find_elements(By.TAG_NAME, "tr") or []
            parsed = []
            for r in rows:
                try:
                    tds = r.find_elements(By.TAG_NAME, "td")
                    if len(tds) < 13: continue
                    folio = (tds[0].text or "").strip()
                    f_txt = (tds[2].text or "").split(" ")[0].strip()
                    deriv = (tds[8].text or "").strip()
                    cod = (tds[9].text or "").strip()
                    diag = (tds[12].text or "").strip()
                    f_dt = dparse(f_txt) or 0
                    parsed.append((f_dt, f_txt, deriv, diag, cod, folio))
                except Exception: continue
            parsed.sort(key=lambda x: x[0] if x[0] else 0, reverse=True)
            if n and n > 0: parsed = parsed[:n]
            return ([p[1] for p in parsed], [p[2] for p in parsed], [p[3] for p in parsed], [p[4] for p in parsed], [p[5] for p in parsed])
        except Exception: return [], [], [], [], []

    def leer_aps_desde_caso(self, root: Any, n: int) -> Tuple[List[str], List[str]]:
        if not root: return [], []
        try:
            tbody = None
            for xp in XPATHS.get("APS_TBODY_FALLBACK", []):
                try:
                    if xp.startswith("/html"): tbody = self.driver.find_element(By.XPATH, xp)
                    else: tbody = root.find_element(By.XPATH, xp.lstrip("."))
                    if tbody:
                        if tbody.find_elements(By.TAG_NAME, "tr"): break
                        tbody = None
                except Exception: continue
            if not tbody:
                p = self._find_section_label_p(root, "Hoja Diaria APS")
                if p: tbody = self._tbody_from_label_p(p)
            if not tbody: return [], []

            rows = tbody.find_elements(By.TAG_NAME, "tr") or []
            parsed = []
            for tr in rows:
                try:
                    tds = tr.find_elements(By.TAG_NAME, "td")
                    if len(tds) < 3: continue
                    fecha_txt = (tds[1].text or "").strip()
                    estado_txt = (tds[2].text or "").strip()
                    if estado_txt and "caso" not in estado_txt.lower(): continue
                    fecha_dt = dparse(fecha_txt) or 0
                    parsed.append((fecha_dt, fecha_txt, estado_txt))
                except Exception: continue
            parsed.sort(key=lambda x: x[0] if x[0] else 0, reverse=True)
            if n and n > 0: parsed = parsed[:n]
            return ([p[1] for p in parsed], [p[2] for p in parsed])
        except Exception: return [], []

    def leer_sic_desde_caso(self, root: Any, n: int) -> Tuple[List[str], List[str]]:
        if not root: return [], []
        try:
            tbody = None
            p = self._find_section_label_p(root, "solicitudes de interconsultas")
            if p: tbody = self._tbody_from_label_p(p)
            if not tbody:
                for xp in XPATHS.get("SIC_TBODY_FALLBACK", []):
                    try:
                        relative = "." + xp.split("/main")[1] if "/main" in xp else xp
                        tbody = root.find_element(By.XPATH, relative)
                        if tbody: break
                    except Exception: continue
            if not tbody: return [], []

            rows = tbody.find_elements(By.TAG_NAME, "tr") or []
            parsed = []
            for tr in rows:
                try:
                    tds = tr.find_elements(By.TAG_NAME, "td")
                    if len(tds) < 9: continue
                    fecha_sic = (tds[2].text or "").strip()
                    derivado = (tds[8].text or "").strip()
                    fecha_dt = dparse(fecha_sic) or 0
                    parsed.append((fecha_dt, fecha_sic, derivado))
                except Exception: continue
            parsed.sort(key=lambda x: x[0] if x[0] else 0, reverse=True)
            if n and n > 0: parsed = parsed[:n]
            return ([p[1] for p in parsed], [p[2] for p in parsed])
        except Exception: return [], []
