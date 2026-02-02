from __future__ import annotations

"""
Reexporta los selectores centralizados en `src/core/locators.py`.

Se mantiene el nombre `XPATHS` para compatibilidad con el código legacy.
"""
from src.core.locators import LOCATORS, XPATHS  # noqa: F401

__all__ = ["LOCATORS", "XPATHS"]
