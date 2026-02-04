import json
import os

config_path = r"C:\Users\usuariohgf\OneDrive\Documentos\Extras\Apps\Proyectos\Nozhgess original\App\config\mission_config.json"

try:
    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for mission in data.get("MISSIONS", []):
        mission["max_objetivos"] = 1
        mission["max_habilitantes"] = 1
        mission["max_excluyentes"] = 1
        mission["max_ipd"] = 1
        mission["max_oa"] = 1
        mission["max_aps"] = 1
        mission["max_sic"] = 1

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Successfully updated mission_config.json")

except Exception as e:
    print(f"Error updating config: {e}")
