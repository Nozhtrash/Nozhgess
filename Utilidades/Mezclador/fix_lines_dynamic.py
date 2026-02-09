
import os

file_path = r"c:\Users\knoth\OneDrive\Documentos\Extras\Apps\Proyectos\Nozhgess original\Utilidades\Mezclador\Conexiones.py"

def fix_dynamic():
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    replacements = {
        'log_error("â” " * 60)': 'log_error("━" * 60)',
        'log_warn(f"â Œ {rut}: Saltado': 'log_warn(f"❌ {rut}: Saltado',
        '# 🔄 CRÃ TICO:': '# 🔄 CRÍTICO:',
        'log_error(f"â Œ Error durante': 'log_error(f"❌ Error durante',
        'log_warn(f"âš ï¸  Paciente': 'log_warn(f"⚠️  Paciente',
        'despuÃ©s': 'después',
        'bÃ¡sicos': 'básicos'
    }
    
    changes = 0
    for i in range(len(lines)):
        line = lines[i]
        for bad, good in replacements.items():
            if bad in line:
                # Replace only the substring to preserve indentation/other context
                lines[i] = lines[i].replace(bad, good)
                print(f"Fixed line {i+1}: {bad} -> {good}")
                changes += 1
    
    # Also check for split-line substrings if necessary, but log messages usually single line
    
    if changes > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"Total changes: {changes}")
    else:
        print("No matches found.")

if __name__ == "__main__":
    try:
        fix_dynamic()
    except Exception as e:
        print(f"Error: {e}")
