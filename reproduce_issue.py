import sys
import os
import datetime

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, "App")
sys.path.insert(0, app_dir)

from src.core.Analisis_Misiones import analizar_misiones

# Mock dependencies
class MockMission:
    def __init__(self, settings):
        self.settings = settings
    
    def get(self, key, default=None):
        return self.settings.get(key, default)
    
    def __getitem__(self, key):
        return self.settings[key]

# Mock global config via sys.modules injection (if needed) or just rely on the fact that we fixed the code to look at 'm' first.
# Analisis_Misiones imports HABILITANTES_MAX from Mision_Actual.
# We need to make sure Mision_Actual is importable.

# Mock Mision_Actual module
import types
ma_mock = types.ModuleType("Mision_Actual")
ma_mock.MISSIONS = []
ma_mock.VENTANA_VIGENCIA_DIAS = 180
ma_mock.REVISAR_HISTORIA_COMPLETA = True
ma_mock.ANIOS_REVISION_MAX = 5
ma_mock.REVISAR_FUTUROS = True
ma_mock.HABILITANTES_MAX = 10 # Global default
ma_mock.EXCLUYENTES_MAX = 10  # Global default
sys.modules["Mision_Actual"] = ma_mock

def test_fix():
    print("Testing Max Habilitantes Fix...")

    # Setup test data
    fecha_nomina = datetime.date(2025, 1, 1)
    rut = "12345678-9"
    nombre = "Juan Perez"
    
    # Create fake cases with habilitantes
    casos = [
        {"codigo": "H001", "fecha": "2024-12-01"},
        {"codigo": "H002", "fecha": "2024-12-02"},
        {"codigo": "H003", "fecha": "2024-12-03"},
    ]
    
    # Mission config with limit 1
    mission_config = {
        "nombre": "Test Mission",
        "familia": "Test",
        "especialidad": "Test",
        "frecuencia": "Mensual",
        "objetivos": [],
        "habilitantes": ["H001", "H002", "H003"],
        "excluyentes": [],
        "max_habilitantes": 1, # LIMIT SET TO 1
        "max_objetivos": 10,
        "max_excluyentes": 10
    }
    
    # Inject fake mission into Mision_Actual.MISSIONS so analizar_misiones picks it up
    ma_mock.MISSIONS = [mission_config]
    
    # Run analysis
    results = analizar_misiones(
        None, # sigges not used in mock mode
        casos,
        fecha_nomina,
        fecha_nomina,
        rut,
        nombre,
        modo_sin_caso=False
    )
    
    # Check results
    row = results[0]
    
    # We expect only Habilitante_1 to be present
    hab_1 = row.get("Habilitante_1")
    hab_2 = row.get("Habilitante_2")
    
    print(f"Habilitante 1: {hab_1}")
    print(f"Habilitante 2: {hab_2}")
    
    if hab_1 and not hab_2:
        print("✅ SUCCESS: Only 1 habilitante found, respecting the limit.")
    elif hab_2:
        print(f"❌ FAILURE: More than 1 habilitante found. Limit ignored.")
    else:
        print("❌ FAILURE: No habilitantes found.")

if __name__ == "__main__":
    test_fix()
