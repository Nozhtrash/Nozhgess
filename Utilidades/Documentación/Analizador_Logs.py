# -*- coding: utf-8 -*-
"""
Analizador de Logs - NOZHGESS "God Mode"
========================================
Este script lee los logs generados por el sistema y aprende de los errores.
Identifica patrones recurrentes, tiempos de espera fallidos y problemas de conexión.

Uso:
    python Analizador_Logs.py
"""
import os
import re
from collections import Counter
from datetime import datetime

# Configuración
# Usar ruta relativa para encontrar la carpeta de Logs
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "Z_Utilidades", "Logs")

def analizar_logs():
    print(f"📊 Analizando logs en {LOG_DIR}...\n")
    
    if not os.path.exists(LOG_DIR):
        print("⚠️ No existe carpeta de logs.")
        return

    archivos_log = [f for f in os.listdir(LOG_DIR) if f.endswith('.log')]
    if not archivos_log:
        print("⚠️ No hay archivos de log para analizar.")
        try:
            # Fallback path check if logs are not found
            fallback_path = os.path.join(os.getcwd(), "logs")
            if os.path.exists(fallback_path):
                 print(f"ℹ️ Verificando ruta alternativa: {fallback_path}")
            else:
                 return
        except:
             return

    errores_totales = []
    advertencias_totales = []
    tiempos_respuesta = []

    for archivo in archivos_log:
        ruta = os.path.join(LOG_DIR, archivo)
        try:
            with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
                for linea in f:
                    # Detectar ERRORES
                    if "[ERROR]" in linea:
                        # Limpiar timestamp y etiquetas para agrupar mensajes similares
                        msg_limpio = re.sub(r'^\d{2}:\d{2}:\d{2} \[ERROR\] ', '', linea).strip()
                        # Eliminar detalles variables (como RUTs o IDs)
                        msg_generico = re.sub(r'\d{7,9}-[\dkK]', '{RUT}', msg_limpio)
                        errores_totales.append(msg_generico)
                    
                    # Detectar WARNINGS
                    elif "[WARN]" in linea:
                        msg_limpio = re.sub(r'^\d{2}:\d{2}:\d{2} \[WARN\] ', '', linea).strip()
                        msg_generico = re.sub(r'\d{7,9}-[\dkK]', '{RUT}', msg_limpio)
                        advertencias_totales.append(msg_generico)
        except Exception as e:
            print(f"Error leyendo {archivo}: {e}")

    # --- Generar Reporte ---
    print("╔══════════════════════════════════════════════════════╗")
    print("║            🧠  INTELIGENCIA DE SISTEMA               ║")
    print("╠══════════════════════════════════════════════════════╣")
    
    # Top Errores
    counter_errores = Counter(errores_totales)
    print(f"║ ❌ Errores Críticos Recurrentes:                     ║")
    if not counter_errores:
        print("║    (Ninguno detectado - Sistema Saludable)           ║")
    else:
        for err, count in counter_errores.most_common(5):
            print(f"║    - [{count}x] {err[:45]:<45}║")

    print("╠══════════════════════════════════════════════════════╣")
    
    # Top Advertencias
    counter_warn = Counter(advertencias_totales)
    print(f"║ ⚠️  Advertencias Frecuentes:                          ║")
    if not counter_warn:
        print("║    (Ninguna detectada)                               ║")
    else:
        for warn, count in counter_warn.most_common(5):
            print(f"║    - [{count}x] {warn[:45]:<45}║")
            
    print("╚══════════════════════════════════════════════════════╝")
    
    # Recomendaciones
    if counter_errores or counter_warn:
        print("\n💡 RECOMENDACIONES DE OPTIMIZACIÓN:")
        if any("spinner" in e.lower() for e in errores_totales):
            print("  👉 Ajustar TIMEOUT_SPINNER en Constants.py (incrementar valor)")
        if any("conexión" in e.lower() for e in errores_totales):
            print("  👉 Revisar estabilidad de internet o incrementar reintentos")
        print("  👉 Revisar los casos específicos en los logs individuales para más detalles.")

if __name__ == "__main__":
    analizar_logs()
