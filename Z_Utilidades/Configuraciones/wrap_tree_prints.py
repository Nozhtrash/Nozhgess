# Script para envolver los prints faltantes de "Expandir caso", "Leer IPD", etc.
import re

file_path = r"c:\Users\usuariohgf\OneDrive\Documentos\Extras\Apps\Proyectos\Nozhgess original\F_Mezclador\Conexiones.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Patrones para los prints faltantes - Buscamos líneas que empiezan con espacios y luego print(f"  └─
# Ejemplo: print(f"  └─ Expandir caso {idx}...")
patterns = [
    r'(\s+)print\(f"\s*└─',  # Captura todos los prints de estructura de árbol
]

for pattern in patterns:
    content = re.sub(
        pattern,
        r'\1if should_show_timing():\n\1    print(f"  └─',
        content
    )

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Prints de estructura de árbol envueltos con should_show_timing()")
