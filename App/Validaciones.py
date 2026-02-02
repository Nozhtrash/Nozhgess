"""
Proxy de Validaciones accesible desde tests e integraciones.

Expone validar_rut, validar_fecha, validar_nombre desde src.utils.Validaciones.
"""
from src.utils.Validaciones import validar_rut, validar_fecha, validar_nombre

__all__ = ["validar_rut", "validar_fecha", "validar_nombre"]
