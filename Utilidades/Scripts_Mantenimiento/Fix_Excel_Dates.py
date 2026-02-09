import pandas as pd
import os
import sys

# Agregar path al proyecto para importar Formatos
# La estructura es: .../Utilidades/Scripts_Mantenimiento/Fix_Excel_Dates.py
# Formatos está en: .../App/src/core/Formatos.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# Subir 2 niveles: .../Utilidades -> .../
project_root = os.path.dirname(os.path.dirname(current_dir))

# Agregar paths para que Python encuentre los módulos
sys.path.insert(0, os.path.join(project_root, "App", "src", "core"))
sys.path.insert(0, os.path.join(project_root, "Z_Utilidades", "Motor")) # Fallback location

try:
    try:
        from Formatos import solo_fecha
    except ImportError:
        # Intentar import relativo si falla el directo
        sys.path.append(os.path.join(project_root))
        from App.src.core.Formatos import solo_fecha
except ImportError as e:
    print(f"Error CRÍTICO: No se pudo importar Formatos. {e}")
    sys.exit(1)

def fix_excel_dates(file_path):
    if not os.path.exists(file_path):
        print(f"Error: El archivo no existe: {file_path}")
        return

    print(f"------------ REPARADOR DE FECHAS ------------")
    print(f"Procesando: {os.path.basename(file_path)}")
    
    try:
        df = pd.read_excel(file_path)
        
        # Identificar columnas de fecha
        cols_modificadas = 0
        
        # 1. Buscar columna 'Fecha' explicita
        if "Fecha" in df.columns:
            print(" -> Detectada columna 'Fecha'")
            df["Fecha"] = df["Fecha"].apply(lambda x: solo_fecha(x))
            cols_modificadas += 1
            
        # 2. Buscar columna A (índice 0) si no es 'Fecha'
        elif len(df.columns) > 0:
            col_0 = df.columns[0]
            print(f" -> Usando primera columna '{col_0}' como fecha")
            df[col_0] = df[col_0].apply(lambda x: solo_fecha(x))
            cols_modificadas += 1
            
        # 3. Buscar otras columnas que parezcan fecha
        for col in df.columns:
            if col == "Fecha" or (len(df.columns) > 0 and col == df.columns[0]):
                continue
            if "fecha" in str(col).lower() or "dob" in str(col).lower() or "nacimiento" in str(col).lower():
                 print(f" -> Detectada columna adicional de fecha: '{col}'")
                 df[col] = df[col].apply(lambda x: solo_fecha(x))
                 cols_modificadas += 1

        if cols_modificadas > 0:
            # Generar nombre salida
            dir_name = os.path.dirname(file_path)
            base_name = os.path.basename(file_path)
            name_part, ext_part = os.path.splitext(base_name)
            output_path = os.path.join(dir_name, f"{name_part}_fixed{ext_part}")
            
            df.to_excel(output_path, index=False)
            print(f"✅ ÉXITO: Archivo guardado en: {output_path}")
        else:
            print("⚠️ Advertencia: No se encontraron columnas de fecha para arreglar.")
            
    except Exception as e:
        print(f"❌ Error procesando el archivo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ruta = sys.argv[1]
        fix_excel_dates(ruta)
    else:
        print("Uso: python Fix_Excel_Dates.py <ruta_completa_excel>")
        print("Ejemplo: python Fix_Excel_Dates.py \"C:\\MiCarpeta\\input.xlsx\"")
