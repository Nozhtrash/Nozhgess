# Utilidades/Principales/ConfigValidator.py
# -*- coding: utf-8 -*-
"""
Validador de Configuración para Nozhgess "Pro".
codificado en utf-8
Verifica que Mision_Actual.py esté saludable antes de iniciar.
"""
import os
from typing import List, Dict, Any
from colorama import Fore, Style
import Mision_Actual.Mision_Actual as config

def validar_configuracion() -> bool:
    """
    Ejecuta todas las validaciones de configuración.
    Retorna True si todo está OK, False si hay errores críticos.
    """
    errores = []
    advertencias = []

    print(f"{Fore.CYAN}🔍 Ejecutando Diagnóstico de Configuración...{Style.RESET_ALL}")

    # 1. Validar Rutas Críticas
    # -------------------------------------------------------------------------
    if not os.path.exists(config.RUTA_ARCHIVO_ENTRADA):
        errores.append(f"❌ Archivo de entrada NO existe: {config.RUTA_ARCHIVO_ENTRADA}")
    
    if not os.path.exists(config.RUTA_CARPETA_SALIDA):
        advertencias.append(f"⚠️ Carpeta de salida NO existe (se intentará crear): {config.RUTA_CARPETA_SALIDA}")
    
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
        advertencias.append("⚠️ Hay índices de columnas repetidos en la configuración de entrada.")

    # Reporte Final
    # -------------------------------------------------------------------------
    if advertencias:
        print(f"\n{Fore.YELLOW}=== ADVERTENCIAS ({len(advertencias)}) ==={Style.RESET_ALL}")
        for adv in advertencias:
            print(f"  {adv}")

    if errores:
        print(f"\n{Fore.RED}=== ERRORES CRÍTICOS DETECTADOS ({len(errores)}) ==={Style.RESET_ALL}")
        for err in errores:
            print(f"  {err}")
        print(f"\n{Fore.RED}⛔ La configuración es inválida. Corrige 'Mision_Actual.py' y reintenta.{Style.RESET_ALL}")
        return False
    
    print(f"{Fore.GREEN}✅ Configuración Validada y Saludable.{Style.RESET_ALL}\n")
    return True
