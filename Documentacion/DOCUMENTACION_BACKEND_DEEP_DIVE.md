# 🛠️ NOZHGESS BACKEND DEEP DIVE v3.5.1
> **Audiencia:** Desarrolladores Core y Arquitectos de Sistema.
> **Enfoque:** Lógica de negocio, manejo de excepciones y estructura de datos.

---

## 1. El Núcleo de Ejecución: `Conexiones.py`

Este archivo no es solo un script; es un orquestador de lógica forense. En v3.5.1, su responsabilidad se ha purificado:

### 1.1 El Ciclo de Vida de un Paciente (`procesar_paciente`)
1.  **Inyección de Dependencias:** Recibe el objeto `sigges` (controlador del navegador) y la fila cruda del Excel.
2.  **Validación Pre-Vuelo:**
    - Verifica formato de RUT (`Normalizador`).
    - Valida fecha (`dparse`). Si son inválidos, retorna falla inmediata (Fail Fast).
3.  **Búsqueda & Resiliencia:** 
    - Intenta buscar el RUT en SIGGES.
    - **Retry Logic:** Si falla (timeout, error de red), reintenta hasta 6 veces con backoff exponencial.
    - **Fatal Error:** Si detecta desconexión del WebSocket (CDP), lanza `FatalConnectionError`.

### 1.2 Motor de Columnas Dinámicas (The "Cols" Engine)
Ubicación: `cols_mision(m)`
- **Antes (Legacy):** Listas estáticas hardcodeadas (`Objetivo_1`...`Objetivo_10`).
- **Ahora (Dynamic):** Itera sobre la configuración `m['objetivos']`, `m['habilitantes']` y `m['excluyentes']`.
- **Resultado:** Retorna una lista de strings que se convierte en la cabecera exacta del DataFrame.

### 1.3 Lógica de Extracción (`analizar_mision`)
Aquí ocurre la magia forense.
- **Extracción de Prestaciones:** `sigges.leer_prestaciones_desde_tbody`.
- **Mapeo de Fechas:** 
    - Crea un diccionario `code -> [fechas]`.
    - Ordena las fechas de más reciente a más antigua.
- **Inyección:**
    - Itera los códigos configurados.
    - Busca en el diccionario.
    - Formatea fechas a `dd-mm-yyyy`.
    - Join con ` | ` si hay múltiples fechas.

---

## 2. El Cerebro Lógico: `Analisis_Misiones.py`

Ubicación: `App/src/core/Analisis_Misiones.py`

### 2.1 FrequencyValidator (V2)
Una clase estática desacoplada.
- **Input:** Lista de prestaciones crudas + Regla de Frecuencia (JSON).
- **Proceso:** 
    - Filtra por código.
    - Convierte fechas a objetos `date`.
    - Calcula delta `(Fecha_Prestación - Fecha_Ref)`.
- **Output:** Diccionario con status (`Cumple`/`No Cumple`) y metadata.

### 2.2 Preservación de "Vigencia" (Hab Vi)
El cálculo de vigencia es *sagrado*.
- **Fórmula:** `(Fecha_Prestación + Ventana_Dias) >= Fecha_Corte`
- **Crítico:** Este cálculo ignora si la columna visual "Hab [Code]" existe o no. Se hace a nivel de datos, garantizando que el semáforo "Vigente/No Vigente" sea siempre veraz.

---

## 3. Manejo de Datos Críticos

### 3.1 Fallecimiento
- **Fuente:** `sigges.leer_fallecimiento()`.
- **Transformación:** Si devuelve `datetime`, se formatea a string. Si es `None`, se asigna "No".
- **Integridad:** Se guarda en la columna "Fallecido" y NUNCA se mezcla con "Observaciones".

### 3.2 Observaciones
- **Política de Limpieza:** El backend inicia la columna vacía `""`.
- **Escritura:** Solo escribe si `sigges` reporta una excepción manejada (ej. `Sin Mini-Tabla`).

---

## 4. Estructura de Datos en Memoria

El sistema mueve diccionarios pesados.
```python
{
    "RUT": "12.345.678-9",
    "Fecha": "2026-02-11",
    "Obj 040101": "12-05-2025 | 10-01-2025", # Dinámico
    "Hab 500210": "15-08-2024",              # Dinámico
    "Hab Vi": "Vigente",                     # Calculado
    "Fallecido": "No",
    "_cols_order": ["RUT", "Nombre" ... ]    # Metadata oculta para el Excel Writer
}
```

---
**© 2026 Nozhgess Dev Team**
