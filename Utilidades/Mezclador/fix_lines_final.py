
import os

file_path = r"c:\Users\knoth\OneDrive\Documentos\Extras\Apps\Proyectos\Nozhgess original\Utilidades\Mezclador\Conexiones.py"

def fix_lines():
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Target lines (1-based from view_file, so subtract 1)
    # 1598: log_error("â” " * 60)
    # 1604: log_error("â” " * 60)
    # 1611: log_warn(f"â Œ {rut}: Saltado tras {intento} intentos")
    # 1619: # 🔄 CRÃ TICO: Refresh completo...
    # 1633: log_error(f"â Œ Error durante refresh post-reintentos: {pretty_error(e)}")
    
    # We need to be careful if line numbers shifted due to previous edits?
    # No, assuming view_file from Step 376 is current.
    
    # Check if lines look like what we expect to avoid shifting errors
    
    def check_and_replace(idx, partial_match, new_content):
        if idx < len(lines) and partial_match in lines[idx]:
            # Preserve indentation
            indent = lines[idx][:lines[idx].find(lines[idx].lstrip())]
            lines[idx] = indent + new_content + "\n"
            print(f"Fixed line {idx+1}")
        else:
            print(f"Skipped line {idx+1}: Content mismatch or out of bounds. Found: {lines[idx].strip()[:20]}...")

    check_and_replace(1597, 'log_error("', 'log_error("━" * 60)') # Line 1598
    check_and_replace(1603, 'log_error("', 'log_error("━" * 60)') # Line 1604
    check_and_replace(1610, 'log_warn', 'log_warn(f"❌ {rut}: Saltado tras {intento} intentos")') # Line 1611
    check_and_replace(1618, '#', '# 🔄 CRÍTICO: Refresh completo para limpiar estado corrupto antes de siguiente paciente') # Line 1619
    check_and_replace(1632, 'log_error', 'log_error(f"❌ Error durante refresh post-reintentos: {pretty_error(e)}")') # Line 1633

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

if __name__ == "__main__":
    try:
        fix_lines()
    except Exception as e:
        print(f"Error: {e}")
