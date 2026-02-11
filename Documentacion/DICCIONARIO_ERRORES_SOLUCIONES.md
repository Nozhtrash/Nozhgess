# 📕 DICCIONARIO DE ERRORES Y SOLUCIONES NIVEL 3 (v3.5.1)
> **Meta:** Reducir el MTTR (Mean Time To Repair) a < 5 minutos.

---

## 1. ERRORES DE CONECTIVIDAD Y DRIVER (CRÍTICOS)

| Código/Mensaje | Causa Raíz | Protocolo de Solución |
| :--- | :--- | :--- |
| **"FatalConnectionError: CDP Session Lost"** | El navegador Edge se cerró manualmente o por crash. | Reiniciar todo el ciclo: Cerrar terminal -> Abrir `Nozhgess.pyw` -> Reiniciar Edge. |
| **"DevToolsActivePort file doesn't exist"** | Conflicto de puertos. Otra instancia de Chrome/Edge usa el 9222. | Ejecutar `taskkill /F /IM msedge.exe` en PowerShell. |
| **"Timeout Exception (30s)"** | SIGGES está saturado o el internet es inestable. | Verificar acceso manual a SIGGES. Si funciona, aumentar `ESPERA_CARGA` en `config.json`. |

---

## 2. ERRORES DE LÓGICA DE NEGOCIO (WARN)

| Mensaje en Log | Significado | Acción del Operador |
| :--- | :--- | :--- |
| **"Sin Mini-Tabla"** | El RUT existe en SIGGES pero no tiene historial GES visible. | Verificar RUT en Excel de entrada. Si es correcto, el paciente no es GES. |
| **"Saltado tras 6 intentos"** | Falló la extracción repetidamente. | Revisar manualmente ese RUT en SIGGES. Posible corrupción de datos en la ficha. |
| **"Columna 'Obj X' vacía"** | El paciente no tiene prestaciones con ese código. | Normal. Significa que no se encontró el objetivo buscado. |

---

## 3. ERRORES DE CONFIGURACIÓN (USER)

| Síntoma | Causa | Solución |
| :--- | :--- | :--- |
| **Excel final sin columnas de Habilitantes** | `habilitantes` vacío en JSON o `require_oa: false`. | Revisar `mission_config.json`. Activar banderas necesarias. |
| **"KeyError: 'objetivos'"** | JSON mal formado. Falta la llave obligatoria. | Validar JSON en `jsonlint.com` y corregir estructura. |
| **Fechas en formato "45321"** | Excel interpretó la fecha como número. | Seleccionar columna en Excel -> Formato de Celdas -> Fecha Corta. |

---

## 4. ERRORES DE AUDITORÍA FORENSE

| Alerta | Interpretación | Gravedad |
| :--- | :--- | :--- |
| **"Fallecido: [Fecha]"** | Paciente murió antes/durante el proceso. | **ALTA.** Verificar si la garantía venció antes del deceso. |
| **"Caso en Contra: [Nombre]"** | Paciente tiene otra patología GES activa. | **MEDIA.** Posible error de ingreso administrativo. Revisar ficha. |
| **Hab Vi: "No Vigente"** | Diagnóstico o examen está vencido (>1 año). | **BAJA.** El paciente requiere re-evaluación antes de ingresar. |

---
**© 2026 Nozhgess Support Ops**
