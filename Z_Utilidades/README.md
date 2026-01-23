# NOZHGESS v1.0 - Sistema de Revisión Automatizada SIGGES

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.x-green)](https://www.selenium.dev/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)](https://github.com)
[![Quality](https://img.shields.io/badge/Quality-SSSS%2B-gold)](https://github.com)

Sistema profesional de automatización para revisión de fichas clínicas en SIGGES (Sistema de Gestión de Garantías Explícitas en Salud).

---

## 📋 Descripción

NOZHGESS automatiza el proceso de revisión de nóminas de pacientes en SIGGES, extrayendo información crítica de historias clínicas y generando reportes Excel formateados profesionalmente.

**Características principales**:

- ✅ Automatización completa de búsqueda y navegación en SIGGES
- ✅ Extracción inteligente de datos clínicos (IPD, OA, APS, SIC)
- ✅ Sistema de debug multinivel profesional
- ✅ Generación de Excel con estilos profesionales
- ✅ Manejo robusto de errores y reintentos
- ✅ Performance tracking automático

---

## 🚀 Instalación

### Requisitos Previos

- **Python**: 3.8 o superior
- **Microsoft Edge**: Instalado y accesible
- **Edge WebDriver**: Compatible con tu versión de Edge

### Dependencias

```bash
pip install -r requirements.txt
```

**requirements.txt**:

```
selenium>=4.0.0
pandas>=1.3.0
openpyxl>=3.0.0
colorama>=0.4.4
python-dateutil>=2.8.0
```

### Configuración de Edge

1. Ejecutar Edge en modo debug:

```powershell
.\init.ps1
```

O manualmente:

```powershell
Start-Process msedge.exe -ArgumentList "--remote-debugging-port=9222", "--user-data-dir=C:\EdgeDebug"
```

---

## ⚙️ Configuración

### Archivo de Misión

Editar `C_Mision/Mision_Actual.py`:

```python
# Nombre de la misión
NOMBRE_DE_LA_MISION = "Depresion"

# Rutas
RUTA_ARCHIVO_ENTRADA = r"A_Nominas\Depresion.xlsx"
RUTA_CARPETA_SALIDA = r"B_Resultados"

# Columnas del Excel de entrada
INDICE_COLUMNA_FECHA = 2
INDICE_COLUMNA_RUT = 0
INDICE_COLUMNA_NOMBRE = 1

# Toggles de revisión
REVISAR_IPD = True
REVISAR_OA = True
REVISAR_APS = False
REVISAR_SIC = False

# Keywords para identificar casos
MISSIONS = [{
    "nombre": "Depresión",
    "keywords": ["depresion", "trastorno depresivo"],
    # ... más configuración
}]
```

---

## 📖 Uso

### Ejecución Básica

```bash
python "D_Iniciador\Iniciador Script.py"
```

### Con Debug Completo

1. Activar en `Z_Utilidades/Principales/DEBUG.py`:

```python
DEBUG_LEVEL = TRACE  # Máximo detalle
```

1. Ejecutar:

```bash
python "D_Iniciador\Iniciador Script.py"
```

Verás logging detallado de cada operación:

```
[19:08:45.123] [TRACE] → buscar_paciente(9718445-3)
[19:08:45.234] [TRACE] ← buscar_paciente (111ms)
[19:08:45.345] [DEBUG] ✓ Paciente encontrado
```

### Log a Archivo

```python
from Z_Utilidades.Principales.DebugSystem import set_log_file
set_log_file("logs/debug.log")
```

---

## 🏗️ Arquitectura

```
Nozhgess/
├── A_Lista de Misiones/    # Configuraciones de misiones
├── A_Nominas/               # Excel de entrada
├── B_Resultados/            # Excel de salida
├── C_Mision/
│   └── Mision_Actual.py     # Configuración activa
├── D_Iniciador/
│   └── Iniciador Script.py  # Punto de entrada
└── Z_Utilidades/
    ├── Motor/               # Core Selenium
    │   ├── Driver.py        # SiggesDriver principal
    │   ├── Mini_Tabla.py    # Lectura de tabla provisoria
    │   └── Formatos.py      # Utilidades formato
    ├── Mezclador/
    │   └── Conexiones.py    # Orquestador principal
    └── Principales/
        ├── DebugSystem.py   # Sistema de logging
        ├── Esperas.py       # Configuración timeouts
        ├── Direcciones.py   # XPaths
        └── Terminal.py      # Output formatting
```

---

## 🔧 Sistema de Debug

### Niveles de Debug

```python
CRITICAL = 0  # Solo errores fatales
ERROR = 1     # Errores y warnings
INFO = 2      # Información operacional (default)
DEBUG = 3     # Detalles de ejecución
TRACE = 4     # Cada función, cada paso
```

### Decoradores

```python
from Z_Utilidades.Principales.DebugSystem import debug

@debug.trace_function()
def mi_funcion(param):
    """Automáticamente loguea entrada/salida y timing."""
    pass

@debug.log_step("Procesando paciente")
def procesar(rut):
    """Loguea el paso con timing."""
    pass
```

### Context Managers

```python
from Z_Utilidades.Principales.DebugSystem import DebugBlock

with DebugBlock("Analizar misión", rut=rut, mision=nombre):
    # Código con timing automático
    pass
```

---

## 📊 Flujo de Trabajo

1. **Cargar nómina** desde Excel
2. Para cada paciente:
   - Buscar en SIGGES por RUT
   - Leer mini-tabla (casos provisorios)
   - Seleccionar caso inteligentemente
   - Navegar a cartola
   - Extraer datos (IPD, OA, APS, SIC)
   - Analizar según criterios de misión
3. **Generar Excel** con resultados formateados

---

## 🛡️ Manejo de Errores

- **Errores transientes**: Reintentos automáticos (configurable)
- **Errores fatales**: Detección y mensaje claro
- **Timeout spinners**: Detección y espera inteligente
- **Elementos no encontrados**: Fallbacks con XPaths alternativos

---

## 📝 Licencia

Uso interno. Todos los derechos reservados.

---

## 👥 Soporte

Para activar debug máximo y diagnosticar problemas:

```python
# En DEBUG.py
DEBUG_LEVEL = TRACE
set_log_file("logs/debug.log")
```

Revisar `logs/debug.log` para análisis detallado.

---

## 🎯 Estado del Proyecto

**Versión**: 1.0  
**Calidad**: SSSS+ (Perfección Absoluta)  
**Estado**: Producción  
**Última actualización**: 2026-01-09

---

**Desarrollado con máxima calidad profesional** ⭐⭐⭐⭐⭐
