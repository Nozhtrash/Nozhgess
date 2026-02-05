import os
import json
import ast
from typing import List, Dict, Any

# Defaults for missing keys
DEFAULTS = {
    "periodicidad": "Mensual",
    "frecuencia": "Mensual",
    "frecuencia_cantidad": 1,
    "vigencia_dias": 180,
    "edad_min": 0,
    "edad_max": 0, # 0 means no limit? No, prefer None if possible, but JSON needs null.
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
    "requiere_ipd": True, # Legacy compat
    "requiere_aps": True, # Legacy compat
    "filtro_folio_activo": False,
    "codigos_folio": [],
    "active_year_codes": False,
    "indices": {
        "rut": 1,
        "nombre": 2,
        "fecha": 10
    },
    "anios_codigo": [],
    "folio_vih": False,
    "folio_vih_codigos": []
}

def extract_list_from_py(file_path: str) -> List[Dict[str, Any]]:
    """Extracts the MISSIONS list from a python file using AST."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        for node in tree.body:
            # Handle standard assignment: MISSIONS = []
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == 'MISSIONS':
                        return ast.literal_eval(node.value)
                        
            # Handle annotated assignment: MISSIONS: List[...] = []
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id == 'MISSIONS':
                    return ast.literal_eval(node.value)
        return []
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

def augment_mission(m: Dict[str, Any]) -> Dict[str, Any]:
    """Ensures mission dict has all required keys with defaults."""
    new_m = m.copy()
    
    # Fill missing keys from DEFAULTS
    for k, v in DEFAULTS.items():
        if k not in new_m:
            new_m[k] = v
        # Ensure sub-dicts like "indices" also have their keys if they exist but are partial?
        # For simplicity, if indices exists, we trust it. If not, we take default.
            
    # Fix Periodicidad logic: If empty or missing, try to derive from Frecuencia
    if not new_m.get("periodicidad"):
        freq = new_m.get("frecuencia", "Mensual").strip()
        new_m["periodicidad"] = freq.capitalize() if freq else "Mensual"
        
    return new_m

def migrate_folder(root_path: str):
    print(f"Scanning {root_path}...")
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            
            # Case 1: Legacy .py file
            if fname.lower().endswith('.py'):
                print(f"  Converting Python: {fname}")
                missions = extract_list_from_py(fpath)
                if not missions:
                    print(f"    No MISSIONS found in {fname}, skipping.")
                    continue
                
                # Convert and Save
                json_fname = fname[:-3] + ".json"
                json_path = os.path.join(dirpath, json_fname)
                
                # Augment
                aug_missions = [augment_mission(m) for m in missions]
                
                # Write JSON
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump({"MISSIONS": aug_missions}, f, indent=2, ensure_ascii=False)
                print(f"    -> Created {json_fname}")

            # Case 2: Existing .json file (Update/Standardize)
            elif fname.lower().endswith('.json'):
                print(f"  Updating JSON: {fname}")
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if "MISSIONS" in data and isinstance(data["MISSIONS"], list):
                        aug_missions = [augment_mission(m) for m in data["MISSIONS"]]
                        data["MISSIONS"] = aug_missions
                        
                        with open(fpath, 'w', encoding='utf-8') as f:
                             json.dump(data, f, indent=2, ensure_ascii=False)
                        print(f"    -> Updated {fname}")
                    else:
                        print(f"    Skipping {fname} (Invalid structure)")
                except Exception as e:
                    print(f"    Error processing {fname}: {e}")

if __name__ == "__main__":
    target_dir = r"c:\Users\usuariohgf\OneDrive\Documentos\Extras\Apps\Proyectos\Nozhgess original\Lista de Misiones"
    migrate_folder(target_dir)
