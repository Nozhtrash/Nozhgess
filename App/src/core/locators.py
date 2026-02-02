"""
Centraliza TODOS los selectores de SIGGES usando como única fuente de verdad
`Biblia Direcciones.txt`.

Reglas:
- Orden de prioridad dentro de cada lista: XPath (preferible) → CSS (#root…)
  → absolutas (/html/body…).
- No se inventan selectores: cada entrada proviene textualmente de la Biblia.
- El spinner se conserva desde la versión previa (no aparece en la Biblia).

Estructura:
  LOCATORS: dict agrupado por sección.
  XPATHS:   dict plano compatible con el código legacy (mismas keys históricas).
"""
from __future__ import annotations
from typing import Dict, List, Any

# ==============================
#  AGRUPACIÓN POR SECCIONES
# ==============================
LOCATORS: Dict[str, Dict[str, List[str]]] = {
    "urls": {
        "BASE_URL": ["https://www.sigges.cl"],
        "LOGIN_URL": ["https://www.sigges.cl/#/login"],
        "LOGIN_SUCCESS_URL": ["https://www.sigges.cl/#/actualizaciones"],
        "BUSQUEDA_URL": ["https://www.sigges.cl/#/busqueda-de-paciente", "https://www.sigges.cl/#/34"],
        "CARTOLA_URL": ["https://www.sigges.cl/#/cartola-unificada-de-paciente", "https://www.sigges.cl/#/161"],
    },
    "login": {
        # User preference: "solo se debería usar xpath full, es más seguro y no suelen cambiarse"
        # Orden: XPath completo → XPath relativo → CSS (último recurso)
        "LOGIN_BTN_INGRESAR": [
            "/html/body/div/div/div[2]/div[1]/form/div[3]/button",  # Full XPath (Biblia: Primary)
            "//*[@id='root']/div/div[2]/div[1]/form/div[3]/button", # Fallback ID
            "//button[contains(.,'Ingresar')]", 
            "//form//button[@type='submit']",
        ],
        "LOGIN_SEL_UNIDAD_HEADER": [
            "/html/body/div/div/div/div/div[1]/div/div[2]/div[1]/div/div[2]/div[1]",  # Full XPath
            "//*[@id=\"root\"]/div/div/div/div[1]/div/div[2]/div[1]/div/div[2]/div[1]",  # XPath con ID
        ],
        "LOGIN_OP_HOSPITAL": [
            "/html/body/div/div/div/div/div[1]/div/div[2]/div[1]/div/div[2]/div[2]/div/p",  # Full XPath
            "//*[@id=\"root\"]/div/div/div/div[1]/div/div[2]/div[1]/div/div[2]/div[2]/div/p",  # XPath con ID
        ],
        "LOGIN_TILE_INGRESO_SIGGES": [
            "/html/body/div/div/div/div/div[1]/div/div[2]/div[2]/div[2]/div[3]/p",  # Full XPath
            "//*[@id=\"root\"]/div/div/div/div[1]/div/div[2]/div[2]/div[2]/div[3]/p",  # XPath con ID
        ],
        "LOGIN_BTN_CONECTAR": [
            "/html/body/div/div/div/div/div[1]/div/div[2]/div[3]/button/p",  # Full XPath
            "//*[@id=\"root\"]/div/div/div/div[1]/div/div[2]/div[3]/button/p",  # XPath con ID
        ],
    },
    "menu": {
        "MENU_CONTENEDOR": [
            "//*[@id='root']/main/div[2]/nav/div[1]",
            "//nav/div[contains(@class, 'cardMenu')]",
        ],
        "BTN_MENU_INGRESO_CONSULTA_CARD": [
            "//*[@id='root']/main/div[2]/nav/div[1]/div[1]/p",
            "/html/body/div/main/div[2]/nav/div[1]/div[1]/p",
            "#root > main > div.navBar.animate__animated.animate__fadeIn.animate__faster > nav > div:nth-child(1) > div.cardNav__title.leftCenter > p",
        ],
        "BTN_MENU_BUSQUEDA": [
            "//*[@id='root']/main/div[2]/nav/div[1]/div[2]/a[1]",
            "/html/body/div/main/div[2]/nav/div[1]/div[2]/a[1]",
            "//a[@href='#/34']",
        ],
        "BTN_MENU_CARTOLA": [
            "//*[@id='root']/main/div[2]/nav/div[1]/div[2]/a[2]/p",
            "/html/body/div/main/div[2]/nav/div[1]/div[2]/a[2]/p",
            "//a[contains(@href,'161')]",
        ],
    },
    "busqueda": {
        "INPUT_RUT": [
            "//*[@id='rutInput']",
            "/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/div/div/input",
            "#rutInput",
        ],
        "BTN_BUSCAR": [
            "//*[@id='root']/main/div[3]/div[3]/div/div/div[1]/div/button/p",
            "/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/button/p",
            "#root > main > div.content.animate__animated.animate__fadeIn.animate__faster > div.contBody.maxW.scroll > div > div > div:nth-child(1) > div > button",
        ],
        "EDAD_PACIENTE": [
            "//*[@id='root']/main/div[3]/div[3]/div/div[1]/div[7]/div[2]/div/p",
            "/html/body/div/main/div[3]/div[3]/div/div[1]/div[7]/div[2]/div/p",
        ],
        "MINI_TABLA_TBODY": [
            "//*[@id='root']/main/div[3]/div[3]/div/div[2]/div/div/table/tbody",
            "/html/body/div/main/div[3]/div[3]/div/div[2]/div/div/table/tbody",
            "#root > main > div.content.animate__animated.animate__fadeIn.animate__faster > div.contBody.maxW.scroll > div > div:nth-child(2) > div > div > table > tbody",
        ],
        "MINI_TABLA_CASE_NOMBRE": [
            "//*[@id='root']/main/div[3]/div[3]/div/div[2]/div/div/table/tbody/tr[1]/td[2]/p",
            "/html/body/div/main/div[3]/div[3]/div/div[2]/div/div/table/tbody/tr[1]/td[2]/p",
        ],
        "MINI_TABLA_CASE_ESTADO": [
            "//*[@id='root']/main/div[3]/div[3]/div/div[2]/div/div/table/tbody/tr[1]/td[4]/p",
            "/html/body/div/main/div[3]/div[3]/div/div[2]/div/div/table/tbody/tr[1]/td[4]/p",
        ],
        "MINI_TABLA_CASE_MOTIVO": [
            "//*[@id='root']/main/div[3]/div[3]/div/div[2]/div/div/table/tbody/tr[1]/td[5]/p",
            "/html/body/div/main/div[3]/div[3]/div/div[2]/div/div/table/tbody/tr[1]/td[5]/p",
        ],
    },
    "cartola": {
        "CARTOLA_NAV_BTN": [
            "//*[@id='root']/main/div[2]/nav/div[1]/div[2]/a[2]/p",
            "/html/body/div/main/div[2]/nav/div[1]/div[2]/a[2]/p",
            "#root > main > div.navBar.animate__animated.animate__fadeIn.animate__faster > nav > div.cardNav.cardOpen > div.cardNav__menu > a.navBar__button.leftCenter.navBar__button__activ > p",
        ],
        "FECHA_FALLECIMIENTO": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[1]/div[2]/div[5]/div[2]/div/p",
            "/html/body/div/main/div[3]/div[2]/div[1]/div[1]/div[2]/div[5]/div[2]/div/p",
        ],
        "TABLA_PROVISORIA_TBODY": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[3]/div/table/tbody",
            "/html/body/div/main/div[3]/div[2]/div[1]/div[3]/div/table/tbody",
            "#root > main > div.content.animate__animated.animate__fadeIn.animate__faster > div.contBody.scroll > div.contBox.maxW > div:nth-child(3) > div > table > tbody",
        ],
        "TABLA_PROVISORIA_CASO": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[3]/div/table/tbody/tr[1]/td[1]",
            "/html/body/div/main/div[3]/div[2]/div[1]/div[3]/div/table/tbody/tr[1]/td[1]",
        ],
        "TABLA_PROVISORIA_CREACION": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[3]/div/table/tbody/tr[1]/td[3]",
            "/html/body/div/main/div[3]/div[2]/div[1]/div[3]/div/table/tbody/tr[1]/td[3]",
        ],
        "TABLA_PROVISORIA_CIERRE": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[3]/div/table/tbody/tr[1]/td[6]",
            "/html/body/div/main/div[3]/div[2]/div[1]/div[3]/div/table/tbody/tr[1]/td[6]",
        ],
        "CHK_HITOS_GES": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div/div/label/input",
            "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div/div/label/input",
            "#root > main > div.content.animate__animated.animate__fadeIn.animate__faster > div.contBody.scroll > div.contBox.maxW > div:nth-child(6) > div:nth-child(1) > div > div > label > input[type=checkbox]",
        ],
        "TABLA_CASOS_CONTAINER": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]",
            "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]",
            "#root > main > div.content.animate__animated.animate__fadeIn.animate__faster > div.contBody.scroll > div.contBox.maxW > div:nth-child(6) > div:nth-child(1) > div.contRow.contRowBox.scrollH",
        ],
        "CASE_ROW_LABEL": [
            "//*[@id=\"root\"]/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[1]/div/label/p",
            "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[1]/div/label/p",
        ],
        "CASE_ROW_LABEL_2": [
            "//*[@id=\"root\"]/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[2]/div/label/p",
            "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[2]/div/label/p",
        ],
        "CASE_ROW_CHECKBOX": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[1]/div/label/input",
            "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[1]/div/label/input",
            "#root > main > div.content.animate__animated.animate__fadeIn.animate__faster > div.contBody.scroll > div.contBox.maxW > div:nth-child(6) > div:nth-child(1) > div.contRow.contRowBox.scrollH > div:nth-child(1) > div > label > input[type=checkbox]",
        ],
    },
    "titulos_tablas": {
        "TITLE_SIC": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[3]/div[2]/div[1]/div/label/p",
        ],
        "TITLE_CIT": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[3]/div[3]/div[1]/div/label/p",
        ],
        "TITLE_IPD": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[3]/div[4]/div[1]/div/label/p",
        ],
        "TITLE_OA": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[3]/div[5]/div[1]/div/label/p",
        ],
        "TITLE_PO": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[3]/div[6]/div[1]/div/label/p",
        ],
        "TITLE_APS": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[3]/div[7]/div[1]/div/label/p",
        ],
        "TITLE_EXCEPCIONES": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[3]/div[8]/div[1]/div/label/p",
        ],
        "TITLE_CIERRE_GES": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[3]/div[9]/div[1]/div/label/p",
        ],
    },
    "tablas_detalle": {
        "SIC_THEAD": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[15]/div[2]/div[2]/div/table/thead",
        ],
        "SIC_TBODY_FALLBACK": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[15]/div[2]/div[2]/div/table/tbody",
            "//div[label/p[contains(., 'Interconsulta')]]/following-sibling::div//table/tbody",
        ],
        "SIC_FECHA": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[15]/div[2]/div[2]/div/table/tbody/tr/td[3]",
        ],
        "SIC_DERIVADA_PARA": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[15]/div[2]/div[2]/div/table/tbody/tr/td[9]",
        ],
        "SIC_DIAGNOSTICO": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[15]/div[2]/div[2]/div/table/tbody/tr/td[10]",
        ],
        "IPD_THEAD": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[15]/div[4]/div[2]/div/table/thead",
        ],
        "IPD_TBODY_FALLBACK": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[15]/div[4]/div[2]/div/table/tbody",
            "//div[label/p[contains(., 'Informes de Proceso')]]/following-sibling::div//table/tbody",
        ],
        "IPD_FECHA": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[15]/div[4]/div[2]/div/table/tbody/tr/td[3]",
        ],
        "IPD_CONFIRMACION": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[15]/div[4]/div[2]/div/table/tbody/tr/td[7]",
        ],
        "IPD_DIAGNOSTICO": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[15]/div[4]/div[2]/div/table/tbody/tr/td[8]",
        ],
        "OA_THEAD": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[10]/div[5]/div[2]/div/table/thead",
        ],
        "OA_TBODY_FALLBACK": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[10]/div[5]/div[2]/div/table/tbody",
            "//div[label/p[contains(., 'Ordenes de')]]/following-sibling::div//table/tbody",
        ],
        "OA_FOLIO": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[10]/div[5]/div[2]/div/table/tbody/tr/td[1]",
        ],
        "OA_FECHA": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[10]/div[5]/div[2]/div/table/tbody/tr/td[3]",
        ],
        "OA_DERIVADA_PARA": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[10]/div[5]/div[2]/div/table/tbody/tr/td[9]",
        ],
        "OA_CODIGO": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[10]/div[5]/div[2]/div/table/tbody/tr/td[10]",
        ],
        "OA_DIAGNOSTICO": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[10]/div[5]/div[2]/div/table/tbody/tr/td[13]",
        ],
        "APS_THEAD": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[10]/div[7]/div[2]/div/table/thead",
        ],
        "APS_TBODY_FALLBACK": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[4]/div[7]/div[2]/div/table/tbody",
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[10]/div[7]/div[2]/div/table/tbody",
            "//div[label/p[contains(., 'Hoja Diaria APS')]]/following-sibling::div//table/tbody",
        ],
        "APS_FECHA": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[10]/div[7]/div[2]/div/table/tbody/tr[1]/td[2]",
        ],
        "APS_ESTADO": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[10]/div[7]/div[2]/div/table/tbody/tr[1]/td[3]",
        ],
        "PRESTACIONES_THEAD": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[15]/div[6]/div[2]/div/table/thead",
        ],
        "PRESTACIONES_TBODY": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[15]/div[6]/div[2]/div/table/tbody",
            "//div[contains(@class, 'contRow') and contains(@class, 'contRowBox')]//table/tbody",
        ],
        "PRESTACIONES_REF_OA": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[15]/div[6]/div[2]/div/table/tbody/tr[1]/td[1]",
        ],
        "CIERRE_GES_THEAD": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[15]/div[9]/div[2]/div/table/thead",
        ],
        "CIERRE_GES_TBODY": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[15]/div[9]/div[2]/div/table/tbody",
        ],
        "CIERRE_GES_FECHA": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[15]/div[9]/div[2]/div/table/tbody/tr/td[3]",
        ],
        "CIERRE_GES_SUBCAUSAL": [
            "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[15]/div[9]/div[2]/div/table/tbody/tr/td[8]",
        ],
    },
    # Spinner (no viene en la Biblia, se conserva el valor previo)
    "spinner": {
        "SPINNER_CSS": "dialog.loading[open], dialog.loading, div.circulo, dialog[open] .circulo",
        "SPINNER_XPATH": [
            "//dialog[contains(@class,'loading')][@open]",
            "/html/body/div/dialog[2]",
        ],
        "SPINNER_DIV": [
            "/html/body/div/dialog[2]/div",
        ],
    },
}


# ==============================
#  COMPATIBILIDAD LEGACY
# ==============================
def _flatten_locators(locators: Dict[str, Dict[str, List[str]]]) -> Dict[str, Any]:
    flat: Dict[str, Any] = {}
    for section, values in locators.items():
        for key, val in values.items():
            # URLs se exponen como string (compatibilidad con driver.get)
            if key.endswith("_URL") or key == "BASE_URL":
                flat[key] = val[0] if isinstance(val, list) else val
                # Mantener fallback opcional para quien lo requiera
                if isinstance(val, list) and len(val) > 1:
                    flat[f"{key}_FALLBACKS"] = val[1:]
            else:
                flat[key] = val
    return flat


XPATHS: Dict[str, Any] = _flatten_locators(LOCATORS)


__all__ = ["LOCATORS", "XPATHS"]
