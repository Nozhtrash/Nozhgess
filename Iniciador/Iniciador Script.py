# Iniciadores/Iniciador Script.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    INICIADOR SCRIPT - NOZHGESS v1.0
==============================================================================
"""
import sys
import os

# Agregar la carpeta raíz del proyecto al path
ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)

# =============================================================================
#                          EJECUTAR REVISIÓN
# =============================================================================

if __name__ == "__main__":
    try:
        from Utilidades.Mezclador.Conexiones import ejecutar_revision
        ejecutar_revision()
    except KeyboardInterrupt:
        print("\n[!] Proceso cancelado por el usuario")
    except Exception as e:
        print(f"\n[!] Error fatal: {e}")
        import traceback
        traceback.print_exc()
