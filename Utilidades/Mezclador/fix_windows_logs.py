
import os

file_path = r"c:\Users\knoth\OneDrive\Documentos\Extras\Apps\Proyectos\Nozhgess original\Utilidades\Mezclador\Conexiones.py"

def fix_windows_logs():
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace Box Drawing characters with ASCII
    # ─ (U+2500) -> -
    # ━ (U+2501) -> =
    # ❌ (U+274C) -> X (or keep if supported? Terminal.py uses emojis so maybe emojis are OK but box chars are not?)
    
    # User said "lo de los logs". Emojis seem to be a feature Nozhgess uses.
    # But box drawing chars often mess up line wrapping or encoding on basic shells.
    
    new_content = content.replace("─", "-")
    new_content = new_content.replace("━", "=")
    
    # Also fix CRÃ TICO if it exists literally
    new_content = new_content.replace("CRÃ TICO", "CRÍTICO")
    new_content = new_content.replace("CRÃ\xa0TICO", "CRÍTICO") # Non-breaking space?

    # Check for any other double-encoded stuff
    # Ã© -> é
    new_content = new_content.replace("Ã©", "é")
    new_content = new_content.replace("Ã³", "ó")
    new_content = new_content.replace("Ã­", "í")
    new_content = new_content.replace("Ã¡", "á")
    new_content = new_content.replace("Ã±", "ñ")
    
    # Cleanup strange space around emojis if needed?
    # "âš ï¸" -> ⚠️
    # If file has literal "âš ï¸", replace it.
    new_content = new_content.replace("âš ï¸", "⚠️")
    
    if new_content != content:
        print("Sanitizing logs for Windows...")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Done.")
    else:
        print("No unsafe characters found (or already fixed).")

if __name__ == "__main__":
    try:
        fix_windows_logs()
    except Exception as e:
        print(f"Error: {e}")
