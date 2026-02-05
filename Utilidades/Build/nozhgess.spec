# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['App\\src\\gui\\app.py'],
    pathex=[],
    binaries=[],
    datas=[('App/src/gui', 'src/gui'), ('Mision_Actual', 'Mision_Actual'), ('Lista de Misiones', 'Lista de Misiones'), ('Utilidades', 'Utilidades'), ('Extras', 'Extras'), ('Iniciador', 'Iniciador')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Nozhgess',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Nozhgess',
)
