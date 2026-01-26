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
    
    # Botón "Ingresar"
    "LOGIN_BTN_INGRESAR": [
        "//*[@id='root']/div/div[2]/div[1]/form/div[3]/button", # User Absolute
        "//button[@type='submit' and contains(@class,'botonBase')]", # User Class
        "//button[.//p[normalize-space()='Ingresar']]",
    ],
    
    # Dropdown "Seleccione una unidad"
    "LOGIN_SEL_UNIDAD_HEADER": [
        "//*[@id='root']/div/div/div/div[1]/div/div[2]/div[1]/div/div[2]/div[1]", # User Absolute
        "//div[contains(@class,'filtroSelect__header')]",
    ],
    
    # Opción hospital "Gustavo Fricke"
    "LOGIN_OP_HOSPITAL": [
        "//*[@id='root']/div/div/div/div[1]/div/div[2]/div[1]/div/div[2]/div[2]/div/p", # User Absolute
        "//div[contains(@class,'filtroSelect__options')]//p[contains(text(),'Gustavo Fricke')]",
    ],
    
    # Tile "INGRESO SIGGES CONFIDENCIAL"
    "LOGIN_TILE_INGRESO_SIGGES": [
        "//*[@id='root']/div/div/div/div[1]/div/div[2]/div[2]/div[2]/div[3]/p", # User Absolute
        "//p[normalize-space()='INGRESO SIGGES CONFIDENCIAL']",
    ],
    
    # Botón "Conectese con unidad y perfil"
    "LOGIN_BTN_CONECTAR": [
        "//*[@id='root']/div/div/div/div[1]/div/div[2]/div[3]/button/p", # User Absolute
        "//button[.//p[contains(text(),'Conectese')]]",
    ],

    # =========================================================================
    #                          MENÚ LATERAL
    # =========================================================================
    "MENU_CONTENEDOR": [
        "//*[@id='root']/main/div[2]/nav/div[1]", # User Absolute
        "//nav/div[contains(@class, 'cardMenu')]",
    ],
    "MENU_ICONO_APERTURA": [
        "//*[@id='root']/main/div[2]/nav/div[1]/div[1]", # User Absolute
        "//nav/div[contains(@class, 'cardMenu')]/div",
    ],
    "MENU_CLASS_ABIERTO": "cardOpen",
    
    # Card "Ingreso y Consulta Paciente" (Abre el menú)
    "BTN_MENU_INGRESO_CONSULTA_CARD": [
        "//*[@id='root']/main/div[2]/nav/div[1]/div[1]/p", # User Absolute (Text)
        "//p[normalize-space()='Ingreso y Consulta Paciente']",
    ],
    
    
    # Botón del menú para ir a Búsqueda de Paciente
    "BTN_MENU_BUSQUEDA": [
        "//*[@id='root']/main/div[2]/nav/div[1]/div[2]/a[1]", # User Absolute
        "//a[@href='#/34']", # User Link Directo
        "//a[.//p[normalize-space()='Búsqueda de Paciente']]",
    ],
    
    # Botón del menú para ir a Cartola
    "BTN_MENU_CARTOLA": [
        "//*[@id='root']/main/div[2]/nav/div[1]/div[2]/a[2]/p", # User Absolute
        "//*[@id='root']/main/div[2]/nav/div[1]/div[2]/a[4]/p", # Alternativo (posible variación)
        "//a[@href='#/161']", # User Link Directo
        "//a[.//p[contains(text(),'Cartola Unificada')]]",
    ],

    # =========================================================================
    #                      BÚSQUEDA DE PACIENTE
    # =========================================================================
    "INPUT_RUT": [
        "//*[@id='rutInput']", # User & Universal
        "//input[@id='rutInput']",
        "/html/body/div/main/div[3]/div[3]/div/div/div[1]/div/div/div/input",
    ],
    # Botón "Buscar RUN"
    "BTN_BUSCAR": [
        "//*[@id='root']/main/div[3]/div[3]/div/div/div[1]/div/button", # User Absolute (to Button - Priority 1)
        "//*[@id='root']/main/div[3]/div[3]/div/div/div[1]/div/button/p", # User Absolute (to P - Priority 2)
        "//button[@class='botonBase botonStand2']", # User Class Specific
        "//button[.//p[normalize-space()='Buscar RUN']]",
        "//button[contains(., 'Buscar')]", # Generic Fallback 1
        "//p[contains(text(), 'Buscar')]/ancestor::button", # Generic Fallback 2
    ],
    "EDAD_PACIENTE": [
        "//*[@id='root']/main/div[3]/div[3]/div/div[1]/div[7]/div[2]/div/p", # User Absolute
        "//div[contains(text(),'Edad')]/following-sibling::div/p",
    ],

    # =========================================================================
    #                          MINI TABLA
    # =========================================================================
    # 🧠 INTELIGENTE: Selectores que priorizan tbody CON filas (no vacío)
    "MINI_TABLA_TBODY": [
        "//*[@id='root']/main/div[3]/div[3]/div/div[2]/div/div/table/tbody", # User Absolute
        "//div[contains(@class,'cardTable')]//table/tbody",
    ],
    "MINI_TABLA_TABLE": [
        "//*[@id='root']/main/div[3]/div[3]/div/div[2]/div/div/table", # User Absolute
    ],

    # =========================================================================
    #                            CARTOLA
    # =========================================================================
    "CONT_CARTOLA": [
        "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]", # Base container
        "//div[contains(@class, 'container-cartola')]",
    ],
    
    # Contenedor principal de filtros (Hitos GES, No GES, Todos)
    "CONT_FILTROS_CARTOLA": [
        "//div[@class='contBox'][@data-color='celeste']",
        "/html/body/div/main/div[3]/div[2]/div[1]/div[5]",
    ],
    
    # Hitos GES
    "CHK_HITOS_GES": [
        "//*[@id='root']/main/div[3]/div[2]/div[1]/div[5]/div[1]/div/div/label/input", # User Absolute
        "//label[input[@type='checkbox']]/p[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'hitos ges')]/..//input",
        "//input[@type='checkbox' and ancestor::label[contains(., 'GES')]]",
    ],
    "CONT_HITOS_GES": [
        "//div[@class='contRow'][@data-color='gris'][.//p[contains(., 'Hitos GES')]]",
        "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]",
    ],
    
    # Tabla Provisoria (Fechas Inicio/Cierre)
    "TABLA_PROVISORIA_TBODY": [
        "//*[@id='root']/main/div[3]/div[2]/div[1]/div[3]/div/table/tbody", # User Absolute
        "//div[contains(@class,'contBox')]//table/tbody",
    ],
    
    # Fecha Fallecimiento
    "FECHA_FALLECIMIENTO": [
        "//*[@id='root']/main/div[3]/div[2]/div[1]/div[1]/div[2]/div[5]/div[2]/div/p", # User Absolute
        "//p[contains(text(),'Sin Información') or contains(text(),'Vivo') or contains(text(),'/')]", 
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
        # XPath absoluto proporcionado por el usuario (más confiable)
        "/html/body/div/main/div[2]/nav/div[1]/div[1]",
        "//div[contains(@class,'cardNav__title')]//p[contains(normalize-space(),'Ingreso y Consulta')]",
        "//p[normalize-space()='Ingreso y Consulta Paciente']",  # Texto exacto
        "//div[contains(@class,'cardNav__title') and contains(@class,'leftCenter')]",
        "//nav/div[contains(@class,'cardMenu')]/div[1]//p",
        "/html/body/div/main/div[2]/nav/div[1]/div[1]/p",  # XPath del texto
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
        "//p[contains(normalize-space(.),'Hoja Diaria APS')]",
        "//p[contains(normalize-space(.),'Hoja Diaria')]"
    ],
    "APS_TBODY_FALLBACK": [
        # Correcto según inspección del usuario (div[2]/div[7])
        "/html/body/div/main/div[3]/div[2]/div[1]/div[5]/div[1]/div[2]/div[2]/div[7]/div[2]/div/table/tbody",
        "//div[label/p[contains(., 'Hoja Diaria APS')]]/following-sibling::div//table/tbody",
        "//p[contains(., 'Hoja Diaria APS')]/ancestor::div[contains(@class,'contRow')]//table/tbody",
        "//p[contains(., 'Hoja Diaria')]/ancestor::div//table/tbody",
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
    "SPINNER_CSS": "dialog.loading[open], dialog.loading, div.circulo, dialog[open] .circulo",
    "SPINNER_XPATH": [
        "//dialog[contains(@class,'loading')][@open]",  # Most precise
        "//dialog[@class='loading']",
        "/html/body/div/dialog[2]", # Absolute
        "//*[@id='root']/dialog[2]", # Fallback Absolute
    ],
    "SPINNER_DIV": [
        "//dialog[@class='loading']/div[@class='circulo']",
        "/html/body/div/dialog[2]/div",
    ],
}
