"""
Proxy de Validaciones para rutas legacy.

Permite importaciones `from Validaciones import ...` resolviendo a
`src.utils.Validaciones` dentro de la carpeta App.
"""
from App.src.utils.Validaciones import validar_rut, validar_fecha, validar_nombre

__all__ = ["validar_rut", "validar_fecha", "validar_nombre"]
