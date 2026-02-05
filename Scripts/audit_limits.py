import sys
import os
import datetime
from unittest.mock import MagicMock

# Add mock module for Z_Utilidades dependencies
import types
z_utils = types.ModuleType("Z_Utilidades")
z_utils.Principales = types.ModuleType("Principales")
z_utils.Principales.DEBUG = types.ModuleType("DEBUG")
z_utils.Principales.DEBUG.should_show_timing = lambda: False
z_utils.Principales.Direcciones = types.ModuleType("Direcciones")
z_utils.Principales.Direcciones.XPATHS = {}
z_utils.Principales.Errores = types.ModuleType("Errores")
z_utils.Principales.Errores.clasificar_error = lambda e, s=True: None
z_utils.Principales.Errores.pretty_error = lambda e: str(e)
z_utils.Principales.Esperas = types.ModuleType("Esperas")
z_utils.Principales.Esperas.espera = lambda x: None
z_utils.Principales.Excel_Revision = types.ModuleType("Excel_Revision")
z_utils.Principales.Excel_Revision.generar_excel_revision = lambda a,b,c,d: None
z_utils.Principales.Terminal = types.ModuleType("Terminal")
z_utils.Principales.Terminal.log_error = lambda x: print(f"ERROR: {x}")
z_utils.Principales.Terminal.log_info = lambda x: print(f"INFO: {x}")
z_utils.Principales.Terminal.log_ok = lambda x: print(f"OK: {x}")
z_utils.Principales.Terminal.log_warn = lambda x: print(f"WARN: {x}")
z_utils.Principales.Terminal.log_debug = lambda x: None
z_utils.Principales.Terminal.mostrar_banner = lambda a,b,c: None
z_utils.Principales.Terminal.mostrar_resumen_final = lambda: None
z_utils.Principales.Terminal.resumen_paciente = lambda *args: None
z_utils.Principales.Timing = types.ModuleType("Timing")
z_utils.Principales.Timing.Timer = MagicMock()
z_utils.Motor = types.ModuleType("Motor")
z_utils.Motor.Driver = types.ModuleType("Driver")
z_utils.Motor.Driver.iniciar_driver = lambda a,b: MagicMock()
z_utils.Motor.Formatos = types.ModuleType("Formatos")
def mock_dparse(d):
    try:
        if isinstance(d, datetime.datetime): return d
        return datetime.datetime.strptime(d, "%d/%m/%Y")
    except: return None
z_utils.Motor.Formatos.dparse = mock_dparse
z_utils.Motor.Formatos._norm = lambda x: str(x).lower().strip()
z_utils.Motor.Formatos.en_vigencia = lambda a,b,c: True
z_utils.Motor.Formatos.has_keyword = lambda a,b: False
z_utils.Motor.Formatos.join_clean = lambda x: " | ".join([str(i) for i in x if i])
z_utils.Motor.Formatos.join_tags = lambda x: ""
z_utils.Motor.Formatos.normalizar_codigo = lambda x: str(x).strip()
z_utils.Motor.Formatos.normalizar_rut = lambda x: x
z_utils.Motor.Formatos.same_month = lambda a,b: False
z_utils.Motor.Formatos.solo_fecha = lambda x: x
z_utils.Motor.Mini_Tabla = types.ModuleType("Mini_Tabla")
z_utils.Motor.Mini_Tabla.leer_mini_tabla = lambda x: []

sys.modules["Z_Utilidades"] = z_utils
sys.modules["Z_Utilidades.Principales"] = z_utils.Principales
sys.modules["Z_Utilidades.Principales.DEBUG"] = z_utils.Principales.DEBUG
sys.modules["Z_Utilidades.Principales.Direcciones"] = z_utils.Principales.Direcciones
sys.modules["Z_Utilidades.Principales.Errores"] = z_utils.Principales.Errores
sys.modules["Z_Utilidades.Principales.Esperas"] = z_utils.Principales.Esperas
sys.modules["Z_Utilidades.Principales.Excel_Revision"] = z_utils.Principales.Excel_Revision
sys.modules["Z_Utilidades.Principales.Terminal"] = z_utils.Principales.Terminal
sys.modules["Z_Utilidades.Principales.Timing"] = z_utils.Principales.Timing
sys.modules["Z_Utilidades.Motor"] = z_utils.Motor
sys.modules["Z_Utilidades.Motor.Driver"] = z_utils.Motor.Driver
sys.modules["Z_Utilidades.Motor.Formatos"] = z_utils.Motor.Formatos
sys.modules["Z_Utilidades.Motor.Mini_Tabla"] = z_utils.Motor.Mini_Tabla
sys.modules["src.utils.ExecutionControl"] = MagicMock()

# Mock Mision_Actual
ma = types.ModuleType("Mision_Actual")
# Define vars used in imports
for var in ["NOMBRE_DE_LA_MISION", "RUTA_ARCHIVO_ENTRADA", "RUTA_CARPETA_SALIDA", 
            "DIRECCION_DEBUG_EDGE", "EDGE_DRIVER_PATH", "INDICE_COLUMNA_FECHA", 
            "INDICE_COLUMNA_RUT", "INDICE_COLUMNA_NOMBRE", "MAX_REINTENTOS_POR_PACIENTE", 
            "MISSIONS", "REVISAR_IPD", "REVISAR_OA", "REVISAR_APS", "REVISAR_SIC", 
            "REVISAR_HABILITANTES", "REVISAR_EXCLUYENTES", "FILAS_IPD", "FILAS_OA", 
            "FILAS_APS", "FILAS_SIC", "HABILITANTES_MAX", "EXCLUYENTES_MAX", 
            "VENTANA_VIGENCIA_DIAS", "OBSERVACION_FOLIO_FILTRADA", "CODIGOS_FOLIO_BUSCAR", 
            "FOLIO_VIH", "FOLIO_VIH_CODIGOS"]:
    setattr(ma, var, None)

# Set defaults
ma.FILAS_IPD = 10
ma.FILAS_OA = 10
ma.FILAS_APS = 10
ma.FILAS_SIC = 10
ma.HABILITANTES_MAX = 10
ma.EXCLUYENTES_MAX = 10
ma.VENTANA_VIGENCIA_DIAS = 180

sys.modules["Mision_Actual"] = ma

# Setup Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, "App"))

# Import Conexiones
try:
    from Utilidades.Mezclador.Conexiones import analizar_mision
except ImportError as e:
    print(f"Failed to import Conexiones: {e}")
    sys.exit(1)

def run_audit():
    print("=== STARTING AUDIT OF MAX LIMITS ===")
    
    # 1. Mock Sigges Driver with plenty of data (5 items each)
    mock_sigges = MagicMock()
    mock_sigges.expandir_caso.return_value = "ROOT_ELEMENT"
    
    # IPD: 5 rows
    mock_sigges.leer_ipd_desde_caso.return_value = (
        ["01/01/2025", "02/01/2025", "03/01/2025", "04/01/2025", "05/01/2025"], # Fechas
        ["Si", "No", "No", "No", "No"], # Estados
        ["D1", "D2", "D3", "D4", "D5"]  # Diagnosticos
    )
    
    # OA: 5 rows
    mock_sigges.leer_oa_desde_caso.side_effect = lambda root, n: (
        ["01/01/2025", "02/01/2025", "03/01/2025", "04/01/2025", "05/01/2025"], # Fechas
        ["P1", "P2", "P3", "P4", "P5"], # Derivados
        ["D1", "D2", "D3", "D4", "D5"], # Diagnosticos
        ["C1", "C2", "C3", "C4", "C5"], # Codigos (also for Habilitantes/Objetivos)
        ["F1", "F2", "F3", "F4", "F5"]  # Folios
    )
    
    # APS: 5 rows
    mock_sigges.leer_aps_desde_caso.return_value = (
        ["01/01/2025", "02/01/2025", "03/01/2025", "04/01/2025", "05/01/2025"], # Fechas
        ["E1", "E2", "E3", "E4", "E5"]  # Estados
    )
    
    # SIC: 5 rows
    mock_sigges.leer_sic_desde_caso.return_value = (
        ["01/01/2025", "02/01/2025", "03/01/2025", "04/01/2025", "05/01/2025"], # Fechas
        ["D1", "D2", "D3", "D4", "D5"]  # Derivados
    )
    
    # Prestaciones (for Habilitantes logic which reads from prestaciones table usually)
    # mock_sigges._prestaciones_tbody.return_value = "TBODY"
    # mock_sigges.leer_prestaciones_desde_tbody.return_value = [
    #     {"codigo": "HAB1", "fecha": "01/01/2025"},
    #     {"codigo": "HAB1", "fecha": "02/01/2025"},
    #     {"codigo": "HAB1", "fecha": "03/01/2025"},
    #     {"codigo": "EXC1", "fecha": "01/01/2025"},
    #     {"codigo": "EXC1", "fecha": "02/01/2025"},
    #     {"codigo": "OBJ1", "fecha": "01/01/2025"},
    #     {"codigo": "OBJ1", "fecha": "02/01/2025"},
    # ]
    # NOTE: Conexiones.py uses `leer_prestaciones_desde_tbody` which returns list of dicts.
    
    # We need to ensure analyzing mission reads this.
    mock_sigges._prestaciones_tbody.return_value = "mock_tbody"
    mock_sigges.leer_prestaciones_desde_tbody.return_value = [
         {"codigo": "HAB1", "fecha": "01/01/2025", "glosa": "G", "ref": "R"},
         {"codigo": "HAB1", "fecha": "02/01/2025", "glosa": "G", "ref": "R"},
         {"codigo": "HAB1", "fecha": "03/01/2025", "glosa": "G", "ref": "R"},
         {"codigo": "EXC1", "fecha": "01/01/2025", "glosa": "G", "ref": "R"},
         {"codigo": "EXC1", "fecha": "02/01/2025", "glosa": "G", "ref": "R"},
         {"codigo": "OBJ1", "fecha": "01/01/2025", "glosa": "G", "ref": "R"},
         {"codigo": "OBJ1", "fecha": "02/01/2025", "glosa": "G", "ref": "R"},
    ]

    # 2. Define Mission Config with ALL LIMITS = 1
    mission_config = {
        "nombre": "Audit Mission",
        "require_ipd": True,
        "require_oa": True,
        "require_aps": True,
        "require_sic": True,
        "habilitantes": ["HAB1"],
        "excluyentes": ["EXC1"],
        "objetivos": ["OBJ1"],
        # LIMITS
        "max_ipd": 1,
        "max_oa": 1,
        "max_aps": 1,
        "max_sic": 1,
        "max_habilitantes": 1,
        "max_excluyentes": 1,
        "max_objetivos": 1
    }
    
    case_data = [{"caso": "Test Case", "estado": "Vigente", "apertura": "01/01/2025", "indice": 0, "fecha_dt": datetime.datetime(2025, 1, 1)}]
    
    # 3. Execution
    print("Running analyze_mision...")
    res = analizar_mision(
        sigges=mock_sigges,
        m=mission_config,
        casos_data=case_data,
        fobj=datetime.datetime(2025, 2, 1),
        fecha="01/02/2025",
        fall_dt=None,
        edad_paciente=30,
        rut="11.111.111-1",
        nombre="Test User"
    )
    
    # 4. Verification Checkers
    def check(label, value, should_be_single):
        # Value is joined by " | " in Conexiones.py usually
        count = len(value.split(" | ")) if value else 0
        status = "✅ PASS" if count == 1 else f"❌ FAIL (Count: {count}, Value: {value})"
        print(f"[{label}] Limit=1 -> {status}")
        return count == 1

    print("\n--- RESULTS ---")
    
    # IPD
    check("IPD", res.get("Fecha IPD", ""), True)
    
    # OA
    check("OA", res.get("Fecha OA", ""), True)
    
    # APS
    check("APS", res.get("Fecha APS", ""), True)
    
    # SIC
    check("SIC", res.get("Fecha SIC", ""), True)
    
    # Habilitantes
    # In Conexiones, habilitantes are joined by " | " if multiple codes, 
    # but separate rows if multiple occurrences of same code? 
    # Conexiones: res["C Hab"] = join_clean(...)
    check("Habilitantes", res.get("F Hab", ""), True)
    
    # Excluyentes
    check("Excluyentes", res.get("F Excluyente", ""), True)
    
    # Objetivos
    # Objectives column is F Obj 1. 
    # If max_objetivos=1, we should only see F Obj 1 and it should contain dates.
    # But wait, looking at Conexiones.py logic for objectives:
    # It sorts objectives by date and slices `obj_info = obj_info[:max_objs]`
    # So if we have multiple objective codes, it limits how many codes we check?
    # Or does it limit dates per objective?
    # Logic: 
    #   obj_info = [(cod, [dts]), (cod, [dts])]
    #   obj_info = obj_info[:max_objs]
    # So it limits the NUMBER OF COLUMNS (Objective Types) populated.
    # In this test we have 1 objective code "OBJ1".
    # And we have multple dates for it.
    # Check if F Obj 1 exists.
    print(f"[Objetivos] F Obj 1 present: {'F Obj 1' in res}")
    print(f"[Objetivos] F Obj 2 present (should not be populated/relevant): {res.get('F Obj 2', 'Empty')}")
    
    # Also verify that inside the cell, we don't hold multiple dates if that was the requirement?
    # The requirement "max habilitantes" typically refers to how many historical records to show.
    # For Habilitantes: `top = habs_found[:filas_hab]` -> Limits records.
    # For Objectives: The code logic I added limits `obj_info` which is list of (code, dates).
    # If the user meant "Max records per objective", that's `listar_fechas_objetivo`.
    # Let's see `Conexiones.py`: `dts = listar_fechas_objetivo(prestaciones, cod, fobj)`
    # This function returns ALL dates.
    # The user request "max obj" usually refers to "Maximo de objetivos a mostrar" (columns) or "Maximo de fechas"?
    # In `mission_config.json`, `max_objetivos` is typically 1 (meaning 1 objective column/type).
    # If the user wants to limit the *dates* shown inside that column, that's a different setting (usually not configurable per mission currently, or maybe `max_objetivos` implies dates?)
    # Wait, existing code `max_habilitantes` restricted the *list of found habilitantes*.
    # Existing code `max_oa` restricted *lines of OA rows*.
    # `max_objetivos` logic I added restricts `obj_info` list.
    # `obj_info` is `[(code1, [dates]), (code2, [dates])]`.
    # If `max_objetivos` = 1, we select top 1 objective code found.
    # If the user meant "Only show 1 date per objective", that might be what "max_objetivos" implies if they are thinking about "1 result".
    # However, for now, verifying that my fix works as implemented (Limit Objective Types) is the first step.
    
    val_obj = res.get("F Obj 1", "")
    print(f"[Objective Value] {val_obj}")

run_audit()
