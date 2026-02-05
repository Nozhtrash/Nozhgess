import json
import os

def normalize_json(file_path, template):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    changed = False
    if "MISSIONS" in data:
        for mission in data["MISSIONS"]:
            for key, default_value in template.items():
                if key not in mission:
                    mission[key] = default_value
                    changed = True
    
    if changed:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    return False

# Plantilla basada en diabetes_mellitus_2.json y Base Reporte.json
template = {
    "nombre": "",
    "keywords": [],
    "objetivos": [],
    "habilitantes": [],
    "excluyentes": [],
    "familia": "",
    "especialidad": "13-13-01",
    "frecuencia": "Mensual",
    "periodicidad": "Mensual",
    "frecuencia_cantidad": 1,
    "vigencia_dias": 180,
    "max_objetivos": 1,
    "max_habilitantes": 1,
    "max_excluyentes": 1,
    "max_ipd": 1,
    "max_oa": 1,
    "max_aps": 1,
    "max_sic": 1,
    "require_ipd": True,
    "require_oa": True,
    "require_aps": False,
    "require_sic": False,
    "show_futures": True,
    "requiere_ipd": True,
    "requiere_aps": True,
    "filtro_folio_activo": False,
    "codigos_folio": [],
    "active_year_codes": False,
    "indices": {"rut": "1", "nombre": "3", "fecha": "5"},
    "anios_codigo": [],
    "folio_vih": False,
    "folio_vih_codigos": [],
    "keywords_contra": [],
    "frecuencias": [],
    "active_frequencies": 0,
    "ruta_entrada": "",
    "ruta_salida": ""
}

base_dir = r"c:\Users\usuariohgf\OneDrive\Documentos\Extras\Apps\Proyectos\Nozhgess original\Lista de Misiones"
subdirs = ["Nóminas", "Reportes", "Base Mision"]

total_updated = 0
for subdir in subdirs:
    dir_path = os.path.join(base_dir, subdir)
    if not os.path.exists(dir_path):
        continue
    for filename in os.listdir(dir_path):
        if filename.endswith(".json"):
            file_path = os.path.join(dir_path, filename)
            if normalize_json(file_path, template):
                print(f"Actualizado: {subdir}/{filename}")
                total_updated += 1

print(f"\nFinalizado. Total de archivos actualizados: {total_updated}")
