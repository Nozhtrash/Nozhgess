# -*- mode: python ; coding: utf-8 -*-
"""
==============================================================================
                    PYINSTALLER SPEC - NOZHGESS v3.0 (OPTIMIZED)
==============================================================================
Configuración optimizada para crear ejecutable standalone.
Sin pygame, tamaño reducido.

Uso:
    pyinstaller nozhgess.spec

Resultado:
    dist/Nozhgess/Nozhgess.exe
"""

import os
import sys

# Rutas
SPEC_DIR = os.path.dirname(os.path.abspath(SPECPATH))
PROJECT_ROOT = os.path.dirname(SPEC_DIR) # La raíz es la carpeta padre de App

block_cipher = None

# Archivos de datos a incluir
datas = [
    # Configuración
    (os.path.join(PROJECT_ROOT, 'Mision Actual'), 'Mision Actual'),
    
    # Extras (VBA, docs)
    (os.path.join(PROJECT_ROOT, 'Extras'), 'Extras'),
    
    # Lista de misiones base
    (os.path.join(PROJECT_ROOT, 'Lista de Misiones', 'Base Mision'), 
     os.path.join('Lista de Misiones', 'Base Mision')),
]

# Filtrar solo los que existen
datas = [(src, dst) for src, dst in datas if os.path.exists(src)]

# Imports ocultos que PyInstaller podría no detectar
hiddenimports = [
    'customtkinter',
    'pandas',
    'openpyxl',
    'selenium',
    'selenium.webdriver',
    'selenium.webdriver.edge.service',
    'selenium.webdriver.edge.options',
    'webdriver_manager',
    'webdriver_manager.microsoft',
    'colorama',
    'psutil',
    'PIL',
]

# Excluir módulos pesados innecesarios
excludes = [
    'matplotlib',
    'numpy.testing',
    'scipy',
    'tkinter.test',
    'pygame',  # No necesario - usamos winsound nativo
    'unittest',
    'email',
    'html',
    'http',
    'xml',
    'pydoc',
]

a = Analysis(
    ['Nozhgess.pyw'],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Nozhgess',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Comprimir con UPX si está disponible
    console=False,  # Sin consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(PROJECT_ROOT, 'assets', 'icon.ico') if os.path.exists(os.path.join(PROJECT_ROOT, 'assets', 'icon.ico')) else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Nozhgess',
)
