# Principales/Direcciones.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                     DIRECCIONES.PY - NOZHGESS v1.0
==============================================================================
Centralización de todos los XPaths y selectores de SIGGES.

Este archivo contiene TODOS los selectores organizados por sección.
Cada selector tiene fallbacks para manejar cambios en el DOM.

Autor: Sistema Nozhgess
==============================================================================
"""
from __future__ import annotations
from typing import Dict, List, Any

# =============================================================================
#                            XPATHS Y SELECTORES
# =============================================================================

XPATHS: Dict[str, Any] = {
    # =========================================================================
    #                              URLs
    # =========================================================================
    "BASE_URL": "https://www.sigges.cl",
    "BUSQUEDA_URL": "https://www.sigges.cl/#/busqueda-de-paciente",
    "CARTOLA_URL": "https://www.sigges.cl/#/cartola-unificada-de-paciente",

    # =========================================================================
    #                             LOGIN
    # =========================================================================
    "LOGIN_URL": "https://www.sigges.cl/#/login",
    "LOGIN_SUCCESS_URL": "https://www.sigges.cl/#/actualizaciones",
    
    # Botón "Ingresar" - Priorizar texto sobre estructura
    "LOGIN_BTN_INGRESAR": [
        "//button[.//p[normalize-space()='Ingresar']]",  # Texto exacto (más estable)
        "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'ingresar')]",
        "//button[@type='submit' and contains(@class,'botonBase')]",
        "/html/body/div/div/div[2]/div[1]/form/div[3]/button",  # Fallback absoluto
    ],
    
    # Dropdown "Seleccione una unidad"
    "LOGIN_SEL_UNIDAD_HEADER": [
        "//div[contains(@class,'filtroSelect__header')]//p[normalize-space()='Seleccione una unidad']/..",
        "//div[contains(@class,'filtroSelect__header')]",
        "//p[contains(translate(normalize-space(.),'ÁÉÍÓÚ','áéíóú'),'seleccione una unidad')]/ancestor::div[contains(@class,'filtroSelect__header')]",
        "/html/body/div/div/div/div/div[1]/div/div[2]/div[1]/div/div[2]/div[1]",
    ],
    
    # Opción hospital "Gustavo Fricke"
    "LOGIN_OP_HOSPITAL": [
        "//p[normalize-space()='Hospital Dr. Gustavo Fricke (Viña del Mar)']",
        "//div[contains(@class,'filtroSelect__option')]//p[contains(normalize-space(),'Gustavo Fricke')]",
        "//div[contains(@class,'filtroSelect__option')][.//p[contains(translate(normalize-space(.),'ÁÉÍÓÚ','áéíóú'),'gustavo fricke')]]",
        "/html/body/div/div/div/div/div[1]/div/div[2]/div[1]/div/div[2]/div[2]/div/p",
    ],
    
    # Tile "INGRESO SIGGES CONFIDENCIAL"
    "LOGIN_TILE_INGRESO_SIGGES": [
        "//p[normalize-space()='INGRESO SIGGES CONFIDENCIAL']",
        "//div[contains(@class,'boxItems__item')]//p[contains(normalize-space(),'SIGGES CONFIDENCIAL')]",
        "//div[contains(@class,'boxItems__item')][.//p[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'confidencial')]]",
        "/html/body/div/div/div/div/div[1]/div/div[2]/div[2]/div[2]/div[3]/p",
    ],
    
    # Botón "Conectese con unidad y perfil"
    "LOGIN_BTN_CONECTAR": [
        "//button[.//p[contains(normalize-space(),'Conectese con unidad y perfil')]]",
        "//button[.//p[contains(translate(normalize-space(.),'ÁÉÍÓÚ','áéíóú'),'conectese')]]",
        "//button[contains(@class,'botonBase')]",
        "/html/body/div/div/div/div/div[1]/div/div[2]/div[3]/button",
    ],

    # =========================================================================
    #                          MENÚ LATERAL
    # =========================================================================
    "MENU_CONTENEDOR": [
        "//nav/div[contains(@class, 'cardMenu')]",
        "/html/body/div/main/div[2]/nav/div[1]"
    ],
    "MENU_ICONO_APERTURA": [
        "/html/body/div/main/div[2]/nav/div[1]/div[1]",  # XPath absoluto proporcionado por el usuario
        "//nav/div[contains(@class, 'cardMenu')]/div",
    ],
    "MENU_CLASS_ABIERTO": "cardOpen",
    
    # Menu completo de navegación
    "MENU_NAV_COMPLETO": [
        "/html/body/div/main/div[2]/nav/div[1]/div[2]",  # XPath absoluto proporcionado por el usuario
        "//div[@class='cardNav__menu']",
    ],

    # =========================================================================
    #                      BÚSQUEDA DE PACIENTE
    # =========================================================================
    "INPUT_RUT": [
        "//input[@id='rutInput']",  # ID específico del input
        "//input[contains(@placeholder,'R.U.T')]",
        "//input[contains(@placeholder,'RUT')]",
        "/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/div/div/input",
    ],
    # Botón "Buscar RUN"
    "BTN_BUSCAR": [
        "//button[.//p[normalize-space()='Buscar RUN']]",  # Texto exacto
        "//button[.//p[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'buscar')]]",
        "//button[@class='botonBase botonStand2']",
        "/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/button",
    ],
    "EDAD_PACIENTE": [
        "//div[p[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'edad')]]/following-sibling::div/p",
        "/html/body/div/main/div[3]/div[3]/div/div[1]/div[7]/div[2]/div/p",
    ],

    # =========================================================================
    #                          MINI TABLA
    # =========================================================================
    # 🧠 INTELIGENTE: Selectores que priorizan tbody CON filas (no vacío)
    "MINI_TABLA_TBODY": [
        # Prioridad 1: tbody que YA tiene filas con td (evita race condition)
        "//div[contains(@class,'cardTable')]//table/tbody[.//tr[td]]",
        "//table[.//tr/td]/tbody[ancestor::div[contains(@class, 'cardTable')]]",
        
        # Prioridad 2: tbody genérico (puede estar vacío aún)
        "//div[@class='contBody maxW scroll']//div[contains(@class,'cardTable')]/table/tbody",
        "//table/tbody[ancestor::div[contains(@class, 'cardTable')]]",
        
        # Fallback: XPath absoluto
        "/html/body/div/main/div[3]/div[3]/div/div[2]/div/div/table/tbody",
    ],
    "MINI_TABLA_TABLE": [
        "//div[@class='contBody maxW scroll']//div[contains(@class,'cardTable')]/table",
        "/html/body/div/main/div[3]/div[3]/div/div[2]/div/div/table",
    ],

    # =========================================================================
    #                            CARTOLA
    # =========================================================================
    "CONT_CARTOLA": [
        "//div[contains(@class, 'container-cartola') or contains(@class, 'contRow')]/parent::div",
        "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]"
    ],
    
    # Contenedor principal de filtros (Hitos GES, No GES, Todos)
    "CONT_FILTROS_CARTOLA": [
        "//div[@class='contBox'][@data-color='celeste']",
        "/html/body/div/main/div[3]/div[2]/div[1]/div[5]",
    ],
    
    # Hitos GES
    "CHK_HITOS_GES": [
        "//label[input[@type='checkbox']]/p[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'hitos ges')]/..//input",
        "//input[@type='checkbox' and ancestor::label[contains(., 'GES')]]",
        "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div/div/label/input",
    ],
    "CONT_HITOS_GES": [
        "//div[@class='contRow'][@data-color='gris'][.//p[contains(., 'Hitos GES')]]",
        "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]",
    ],
    
    # Hitos No GES
    "CONT_HITOS_NO_GES": [
        "//div[@class='contRow'][@data-color='gris'][.//p[contains(., 'Hitos No GES')]]",
        "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[2]",
    ],
    
    # Botón del menú para ir a Cartola
    "BTN_MENU_CARTOLA": [
        "//nav//a[contains(@href,'cartola')]",
        "//a[contains(@href, 'cartola-unificada')]",
        "//a[@href='#/161']",  # Link directo
        "/html/body/div/main/div[2]/nav/div[1]/div[2]/a[4]",  # Posición actualizada
        "/html/body/div/main/div[2]/nav/div[1]/div[2]/a[2]",  # Fallback antiguo
        "/html/body/div/main/div[2]/nav/div[1]/div[2]/a[4]/p",
    ],
    
    # Card "Ingreso y Consulta Paciente" - para abrir el menú
    "BTN_MENU_INGRESO_CONSULTA_CARD": [
        "//p[normalize-space()='Ingreso y Consulta Paciente']",  # Texto exacto
        "//div[contains(@class,'cardNav__title')]//p[contains(normalize-space(),'Ingreso y Consulta')]",
        "//nav/div[contains(@class,'cardMenu')]/div[1]//p",
        "/html/body/div/main/div[2]/nav/div[1]/div[1]/p",  # XPath absoluto del Word
    ],
    
    # Botón del menú para ir a Búsqueda de Paciente
    "BTN_MENU_BUSQUEDA": [
        "//a[.//p[normalize-space()='Búsqueda de Paciente']]",  # Texto exacto (más estable)
        "//a[contains(@href,'busqueda-de-paciente')]",
        "//nav//a[contains(@href,'busqueda')]",
        "//a[@href='#/34']",
        "/html/body/div/main/div[2]/nav/div[1]/div[2]/a[1]",  # XPath absoluto
        "/html/body/div/main/div[2]/nav/div[1]/div[2]/a[1]/p",  # Proporcionado por el usuario
    ],

    # =========================================================================
    #                    PRESTACIONES (dentro de un caso)
    # =========================================================================
    "PRESTACIONES_TABLE": [
        "//div[contains(@class, 'contRow') and contains(@class, 'contRowBox')]//table",
        "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[1]/div[6]/div[2]/div/table",
    ],
    "PRESTACIONES_TBODY": [
        "//div[contains(@class, 'contRow') and contains(@class, 'contRowBox')]//table/tbody",
        "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[1]/div[6]/div[2]/div/table/tbody",
    ],

    # =========================================================================
    #                        IPD - FALLBACKS
    # =========================================================================
    "IPD_TBODY_FALLBACK": [
        "//div[label/p[contains(., 'Informes de Proceso')]]/following-sibling::div//table/tbody",
        "//p[contains(., 'Informes de Proceso')]/ancestor::div[contains(@class, 'card') or contains(@class, 'box')]//table/tbody",
        "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[2]/div[4]/div[2]/div/table/tbody",
    ],

    # =========================================================================
    #                        OA - FALLBACKS
    # =========================================================================
    "OA_TBODY_FALLBACK": [
        "//div[label/p[contains(., 'Ordenes de')]]/following-sibling::div//table/tbody",
        "//p[contains(., 'Ordenes de')]/ancestor::div//table/tbody",
        "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div/div[5]/div[2]/div/table/tbody",
    ],

    # =========================================================================
    #                        APS - FALLBACKS
    # =========================================================================
    "APS_LABEL": [
        "//label/p[contains(normalize-space(.),'Hoja Diaria APS')]",
        "//p[contains(normalize-space(.),'Hoja Diaria APS')]"
    ],
    "APS_TBODY_FALLBACK": [
        "//div[label/p[contains(., 'Hoja Diaria APS')]]/following-sibling::div//table/tbody",
        "//p[contains(., 'Hoja Diaria APS')]/ancestor::div//table/tbody",
        "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[16]/div[7]/div[2]/div/table/tbody"
    ],

    # =========================================================================
    #                        SIC - FALLBACKS
    # =========================================================================
    "SIC_TBODY_FALLBACK": [
        "//div[label/p[contains(., 'Interconsulta')]]/following-sibling::div//table/tbody",
        "//p[contains(., 'Interconsulta')]/ancestor::div//table/tbody",
        "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[1]/div[2]/div[2]/div/table/tbody",
    ],

    # =========================================================================
    #                           SPINNER
    # =========================================================================
    "SPINNER_CSS": "dialog.loading",
    "SPINNER_XPATH": [
        "//dialog[@class='loading']",
        "/html/body/div/dialog[2]",
    ],
    "SPINNER_DIV": [
        "//dialog[@class='loading']/div[@class='circulo']",
        "/html/body/div/dialog[2]/div",
    ],
}
