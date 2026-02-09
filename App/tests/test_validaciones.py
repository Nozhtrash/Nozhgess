# tests/test_validaciones.py
# -*- coding: utf-8 -*-
"""
Unit tests for Validaciones module.
Tests RUT validation, date validation, and name validation.
"""
import pytest
from datetime import datetime
# Import corregido para compatibilidad IDE y App
import sys
from pathlib import Path

# Agregar paths para imports relativos
app_root = Path(__file__).parent.parent
sys.path.insert(0, str(app_root))
sys.path.insert(0, str(app_root.parent / "Z_Utilidades" / "Principales"))

try:
    from Validaciones import (
        validar_rut,
        validar_fecha,
        validar_nombre,
    )
except ImportError:
    # Fallback para IDE
    from Z_Utilidades.Principales.Validaciones import (
        validar_rut,
        validar_fecha,
        validar_nombre,
    )


class TestValidarRut:
    """Tests for Chilean RUT validation."""
    
    def test_rut_valido_con_puntos_y_guion(self):
        """RUT válido con formato completo."""
        ok, normalized = validar_rut("12.345.678-5")
        assert ok is True
        assert normalized == "12345678-5"
    
    def test_rut_valido_sin_puntos(self):
        """RUT válido sin puntos."""
        ok, normalized = validar_rut("12345678-5")
        assert ok is True
        assert normalized == "12345678-5"
    
    def test_rut_valido_con_k_minuscula(self):
        """RUT válido con dígito verificador K minúscula."""
        ok, normalized = validar_rut("16.727.694-k")
        assert ok is True
        assert normalized == "16727694-K"  # Normalizado a mayúscula
    
    def test_rut_valido_con_k_mayuscula(self):
        """RUT válido con dígito verificador K mayúscula."""
        ok, normalized = validar_rut("16.727.694-K")
        assert ok is True
        assert normalized == "16727694-K"
    
    def test_rut_dv_incorrecto(self):
        """RUT con dígito verificador incorrecto."""
        ok, normalized = validar_rut("12345678-0")
        assert ok is False
        assert normalized == ""
    
    def test_rut_vacio(self):
        """RUT vacío."""
        ok, normalized = validar_rut("")
        assert ok is False
        assert normalized == ""
    
    def test_rut_none(self):
        """RUT None."""
        ok, normalized = validar_rut(None)
        assert ok is False
        assert normalized == ""
    
    def test_rut_solo_numeros(self):
        """RUT sin guión (inválido)."""
        ok, normalized = validar_rut("12345678")
        assert ok is False
    
    def test_rut_muy_corto(self):
        """RUT demasiado corto."""
        ok, normalized = validar_rut("123-4")
        assert ok is False
    
    def test_rut_con_letras(self):
        """RUT con letras en el cuerpo (inválido)."""
        ok, normalized = validar_rut("12.345.ABC-5")
        assert ok is False


class TestValidarFecha:
    """Tests for date validation."""
    
    def test_fecha_valida(self):
        """Fecha válida en formato DD-MM-YYYY."""
        ok, dt = validar_fecha("15-06-2025")
        assert ok is True
        assert dt.day == 15
        assert dt.month == 6
        assert dt.year == 2025
    
    def test_fecha_primer_dia_mes(self):
        """Fecha del primer día del mes."""
        ok, dt = validar_fecha("01-01-2025")
        assert ok is True
        assert dt.day == 1
        assert dt.month == 1
    
    def test_fecha_ultimo_dia_mes(self):
        """Fecha del último día del mes."""
        ok, dt = validar_fecha("31-12-2025")
        assert ok is True
        assert dt.day == 31
        assert dt.month == 12
    
    def test_fecha_dia_invalido(self):
        """Día inválido (32)."""
        ok, dt = validar_fecha("32-01-2025")
        assert ok is False
        assert dt is None
    
    def test_fecha_mes_invalido(self):
        """Mes inválido (13)."""
        ok, dt = validar_fecha("15-13-2025")
        assert ok is False
        assert dt is None
    
    def test_fecha_febrero_29_bisiesto(self):
        """29 de febrero en año bisiesto."""
        ok, dt = validar_fecha("29-02-2024")  # 2024 es bisiesto
        assert ok is True
        assert dt.day == 29
    
    def test_fecha_febrero_29_no_bisiesto(self):
        """29 de febrero en año no bisiesto (inválido)."""
        ok, dt = validar_fecha("29-02-2025")  # 2025 no es bisiesto
        assert ok is False
    
    def test_fecha_vacia(self):
        """Fecha vacía."""
        ok, dt = validar_fecha("")
        assert ok is False
        assert dt is None
    
    def test_fecha_formato_incorrecto(self):
        """Fecha en formato incorrecto."""
        ok, dt = validar_fecha("2025-06-15")  # ISO format
        assert ok is False
    
    def test_fecha_con_espacios(self):
        """Fecha con espacios extra."""
        ok, dt = validar_fecha("  15-06-2025  ")
        assert ok is True
    
    def test_fecha_muy_antigua(self):
        """Fecha muy antigua (antes de 1900)."""
        ok, dt = validar_fecha("01-01-1899")
        assert ok is False
    
    def test_fecha_muy_futura(self):
        """Fecha muy futura (después de 2100)."""
        ok, dt = validar_fecha("01-01-2101")
        assert ok is False


class TestValidarNombre:
    """Tests for name validation."""
    
    def test_nombre_valido_simple(self):
        """Nombre válido simple."""
        ok, normalized = validar_nombre("Juan Pérez")
        assert ok is True
        assert normalized == "Juan Pérez"
    
    def test_nombre_con_tildes(self):
        """Nombre con acentos y tildes."""
        ok, normalized = validar_nombre("María José García")
        assert ok is True
    
    def test_nombre_con_enie(self):
        """Nombre con ñ."""
        ok, normalized = validar_nombre("Ñoño Muñoz")
        assert ok is True
    
    def test_nombre_con_espacios_extra(self):
        """Nombre con espacios extra al inicio/final."""
        ok, normalized = validar_nombre("  Pedro González  ")
        assert ok is True
        assert normalized == "Pedro González"
    
    def test_nombre_muy_corto(self):
        """Nombre demasiado corto (1 caracter)."""
        ok, normalized = validar_nombre("A")
        assert ok is False
    
    def test_nombre_solo_numeros(self):
        """Nombre que solo contiene números (inválido)."""
        ok, normalized = validar_nombre("12345")
        assert ok is False
    
    def test_nombre_vacio(self):
        """Nombre vacío."""
        ok, normalized = validar_nombre("")
        assert ok is False
    
    def test_nombre_none(self):
        """Nombre None."""
        ok, normalized = validar_nombre(None)
        assert ok is False
