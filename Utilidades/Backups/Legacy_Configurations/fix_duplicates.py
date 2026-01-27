# Script para limpiar duplicados y anidamiento
import re

file_path = r"c:\Users\usuariohgf\OneDrive\Documentos\Extras\Apps\Proyectos\Nozhgess original\F_Mezclador\Conexiones.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Eliminar import duplicado dentro de procesar_paciente
content = re.sub(
    r'\s*# Import DEBUG_MODE\s*\n\s*from Utilidades.Principales\.DEBUG import should_show_timing\s*\n',
    '',
    content
)[1:]  # El [1:] es para quitar el primer match (queremos mantener el del top)

# Arreglar if anidados duplicados
content = re.sub(
    r'if should_show_timing\(\):\s*\n\s*if should_show_timing\(\):\s*\n',
    'if should_show_timing():\n',
    content
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Duplicados eliminados")
