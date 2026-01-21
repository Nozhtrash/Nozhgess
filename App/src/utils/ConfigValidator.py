# Utilidades/Principales/ConfigValidator.py
# -*- coding: utf-8 -*-
"""
Validador de Configuración para Nozhgess "Pro".
codificado en utf-8
Verifica que Mision_Actual.py esté saludable antes de iniciar.
"""
import os
from typing import List, Tuple
from colorama import Fore, Style
import Mision_Actual.Mision_Actual as config

def validar_configuracion() -> Tuple[bool, List[str]]:
    """
    Ejecuta todas las validaciones de configuración.
    Returns:
        tuple: (exito: bool, lista_mensajes: List[str])
    """
    errores = []
    advertencias = []
    mensajes_log = []

    mensajes_log.append("🔍 Ejecutando Diagnóstico de Configuración...")

    # 1. Validar Rutas Críticas
    # -------------------------------------------------------------------------
    if not os.path.exists(config.RUTA_ARCHIVO_ENTRADA):
        errores.append(f"❌ Archivo de entrada NO existe: {config.RUTA_ARCHIVO_ENTRADA}")
    
    # 2. Validar Tipos de Datos (Prevención de Crashes)
    # -------------------------------------------------------------------------
    chequeos_tipos = [
        ("MAX_REINTENTOS_POR_PACIENTE", config.MAX_REINTENTOS_POR_PACIENTE, int),
        ("VENTANA_VIGENCIA_DIAS", config.VENTANA_VIGENCIA_DIAS, int),
        ("REVISAR_IPD", config.REVISAR_IPD, bool),
        ("REVISAR_OA", config.REVISAR_OA, bool),
        ("MISSIONS", config.MISSIONS, list)
    ]

    for nombre, valor, tipo_esperado in chequeos_tipos:
        if not isinstance(valor, tipo_esperado):
            errores.append(f"❌ Error de Tipo en '{nombre}': Se espera {tipo_esperado.__name__}, se encontró {type(valor).__name__}")

    # 3. Validar Estructura de Misiones
    # -------------------------------------------------------------------------
    if not config.MISSIONS:
        errores.append("❌ La lista de Misiones (MISSIONS) está vacía.")
    else:
        for i, mision in enumerate(config.MISSIONS):
            if not isinstance(mision, dict):
                errores.append(f"❌ Misión #{i+1} no es un diccionario válido.")
                continue
            
            # Chequear llaves obligatorias
            keys_obligatorias = ["nombre", "keywords", "familia", "especialidad"]
            for k in keys_obligatorias:
                if k not in mision:
                    errores.append(f"❌ Misión #{i+1} ('{mision.get('nombre', 'Sin Nombre')}') le falta la llave obligatoria: '{k}'")
            
            # Chequear que keywords sea lista
            if "keywords" in mision and not isinstance(mision["keywords"], list):
                errores.append(f"❌ Misión #{i+1}: 'keywords' debe ser una lista de textos.")

    # 4. Validar Índices de Columnas
    # -------------------------------------------------------------------------
    columnas = [config.INDICE_COLUMNA_RUT, config.INDICE_COLUMNA_FECHA, config.INDICE_COLUMNA_NOMBRE]
    if len(set(columnas)) != len(columnas):
        advertencias.append("⚠️ Hay índices de columnas repetidos en la configuración.")

    # Reporte Final
    # -------------------------------------------------------------------------
    todos_los_mensajes = mensajes_log + advertencias + errores
    
    if errores:
        return False, errores
    
    if advertencias:
        return True, advertencias
        
    return True, []
