# Script para envolver TODOS los timing prints con DEBUG_MODE
import re

file_path = r"c:\Users\usuariohgf\OneDrive\Documentos\Extras\Apps\Proyectos\Nozhgess original\F_Mezclador\Conexiones.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Ocultar "Timer global iniciado"
content = re.sub(
    r'(\s+)print\(f".*Timer global iniciado.*"\)',
    r'\1if should_show_timing():\n\1    print(f"{Fore.YELLOW}⏱️ Timer global iniciado - timing acumulativo continuo{Style.RESET_ALL}\\n")',
    content
)

# 2. Envolver todos los prints de "⏳ [rut]" (inicio de timing)
content = re.sub(
    r'(\s+)print\(f"\{Fore\.CYAN\}⏳ \[',
    r'\1if should_show_timing():\n\1    print(f"{Fore.CYAN}⏳ [',
    content
)

# 3. Envolver todos los prints de "✓ [rut]" (fin de timing)  
content = re.sub(
    r'(\s+)print\(f"\{color\}✓ \[',
    r'\1if should_show_timing():\n\1    print(f"{color}✓ [',
    content
)

# 4. Envolver prints de sub-pasos como "└─ Expandir caso"
content = re.sub(
    r'(\s+)print\(f"  └─',
    r'\1if should_show_timing():\n\1    print(f"  └─',
    content
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Timing prints envueltos con should_show_timing()")
