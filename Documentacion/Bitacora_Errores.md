# 🐛 Bitácora de Errores Críticos y Soluciones (Post-Morten)

Este documento detalla los problemas técnicos complejos enfrentados durante el desarrollo, cómo se diagnosticaron y la solución definitiva implementada. Sirve como base de conocimiento para futuros mantenimientos.

---

## 1. El misterio de "Sin Caso" (Fallo de Keywords)

### 🔴 El Problema
El robot detectaba correctamente la cantidad de casos en la "Mini-Tabla" (ej: `✅ 4 caso(s) encontrado(s)`), pero al momento de seleccionar uno, los descartaba todos y reportaba `⚠️ Sin Caso ⚠️`.

**Síntoma:**
```
17:59:29 [INFO] 17472199-8: ✅ 4 caso(s) encontrado(s)
...
[DEBUG] ❌ 'cáncer cervicouterino...' descartado (No contiene ["['Cáncer Cervicouterino'", "'Cáncer Cervicouterino Segmento']"])
```

### 🔍 Diagnóstico (Root Cause Analysis)
Gracias a la instrumentación de logs de diagnóstico en `Conexiones.py`, descubrimos que la lista de palabras clave estaba **doblemente serializada**.

*   **Lo que el código esperaba:** `["Cáncer", "Tumor"]` (Lista de strings)
*   **Lo que había en memoria:** `["['Cáncer', 'Tumor']"]` (Lista de 1 string con corchetes dentro)

Esto ocurrió porque, al guardar desde el Panel de Control, si el usuario pegaba una lista de Python (ej: copiada de un chat), el sistema la guardaba literalmente como una cadena con corchetes.

El comparador buscaba si la cadena `['Cáncer` estaba dentro de `Cáncer Cervicouterino...`. Obviamente fallaba.

### ✅ Solución ("Sanitización Robusta")
Se implementaron dos capas de seguridad:
1.  **Corrección de Datos:** Se editó manualmente `mission_config.json` para limpiar la corrupción.
2.  **Blindaje en `control_panel.py`:** Se modificó el método `_gather_form_data` para limpiar agresivamente cualquier input.

```python
# Solución en código (control_panel.py)
clean_val = val.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
val = [x.strip() for x in clean_val.split(",") if x.strip()]
```
Ahora, aunque el usuario pegue basura con formato de código, el sistema lo convierte en una lista limpia y válida.

---

## 2. Caos en las Terminales (Mezcla de Logs)

### 🔴 El Problema
Las terminales "Debug", "General" y "Principal" mostraban información redundante, faltante o cruzada.
*   "Terminal Debug" estaba muda o mezclada con la General.
*   "Terminal General" (que debe ser un espejo del archivo log) estaba filtrando información técnica vital.

### 🔍 Diagnóstico
El sistema de logs tiene una arquitectura de doble flujo:
1.  **Stdout (Pantalla):** Capturado por `runner.py` para mostrar en vivo.
2.  **Logging (Archivo):** Capturado por un `Handler` especial.

El error fue implementar filtros de "No molestar" en `Terminal.py` (`if DEBUG_MODE:`) que impedían que los mensajes llegaran al flujo de Stdout, dejando a la Terminal Debug sin insumo. Además, un intento previo de limpiar la Terminal General borró accidentalmente mensajes de error críticos.

### ✅ Solución (Arquitectura Estricta)
Se reescribió la lógica de ruteo (`_poll_logs`) en `runner.py` siguiendo una política de "Exclusión Mutua" y "Responsabilidad Única":

| Terminal | Fuente de Datos | Filtro (Prefijos) | Propósito |
| :--- | :--- | :--- | :--- |
| **Principal** | Stdout | `🔥`, `📊`, `📋`, `🤹🏻` | Visión Gerencial (Solo Negocio) |
| **Debug** | Stdout | `⏳`, `✓`, `⏱️`, `[DEBUG]` | Visión Técnica (Tiempos y Pasos) |
| **General** | Logging Handler | Todo (`level == "FILE"`) | Registro Forense Completo |

Se eliminaron los bloqueos en `Terminal.py` para que **siempre** envíe la data, delegando el filtrado a la interfaz gráfica.

---

## 3. Error de Indentación en Producción

### 🔴 El Problema
```python
IndentationError: unexpected indent (Conexiones.py, line 172)
```

### 🔍 Diagnóstico
Durante la inyección de logs de diagnóstico para el problema "Sin Caso", se borró accidentalmente una línea `if score > mejor_puntaje:`, dejando el bloque de asignación huérfano y mal indentado.

### ✅ Solución
Restauración inmediata de la lógica condicional y revisión de sintaxis antes de desplegar.

---

## 4. Puntos Débiles y Mejoras Futuras

### ⚠️ Debilidades Actuales
1.  **Dependencia de `Sys.stdout`:** Capturar la salida estándar es frágil. Si alguna librería ajena hace `print()`, podría aparecer en la terminal debug.
2.  **Copy-Paste en Panel de Control:** Aunque está sanitizado, la UX de tener que pegar listas separadas por comas es propensa a errores humanos.

### 🚀 Mejoras Propuestas
1.  **Canal de Debug Dedicado:** Usar `Queue` directa para eventos de debug en lugar de parsear texto de stdout.
2.  **Validación en Tiempo Real:** Que el Panel de Control muestre "Error de formato" en rojo si detecta corchetes antes de guardar.
3.  **Base de Datos SQLite:** Reemplazar el archivo JSON y los logs de texto por una base de datos real para consultas históricas y analíticas.

---

## 📄 Cómo volver a una versión funcional
Si todo falla catastróficamente:
1.  Restaurar `App/config/mission_config.json` desde un backup (o revisar que no tenga "dobles comillas de listas").
2.  Asegurar que `App/src/gui/views/runner.py` tenga el diccionario `term_prefixes` y `debug_prefixes` correctamente definidos.
