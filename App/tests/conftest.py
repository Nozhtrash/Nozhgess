# tests/conftest.py
# -*- coding: utf-8 -*-
"""
Pytest configuration and fixtures for Nozhgess tests.
"""
import sys
import os

# Add project root to path
ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ruta_proyecto not in sys.path:
    sys.path.insert(0, ruta_proyecto)
