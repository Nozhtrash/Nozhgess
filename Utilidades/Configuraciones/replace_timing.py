# Script temporal para cambiar timing de por-paciente a global
import re

file_path = r"c:\Users\usuariohgf\OneDrive\Documentos\Extras\Apps\Proyectos\Nozhgess original\F_Mezclador\Conexiones.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Cambiar firma de función
content = re.sub(
    r'def procesar_paciente\(sigges, row, idx: int, total: int\)',
    'def procesar_paciente(sigges, row, idx: int, total: int, t_script_inicio: float)',
    content
)

# 2. Comentar la línea que inicializa t_paciente_inicio
content = re.sub(
    r'(\s+)t_paciente_inicio = time\.time\(\)',
    r'\1# t_paciente_inicio = time.time()  # CAMBIADO A GLOBAL\n\1t_paciente_inicio = t_script_inicio  # Usar timer global',
    content
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Timing cambiado a GLOBAL")
