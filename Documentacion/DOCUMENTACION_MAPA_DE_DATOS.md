# 🗺️ NOZHGESS: MAPA DE DATOS Y OBJETIVOS DE SCRAPING v3.5.1
> **Objetivo:** Definir con precisión quirúrgica qué datos extrae el robot y de dónde vienen.

---

## 1. FUENTES DE DATOS PRIMARIAS (SIGGES)

El robot extrae información de 4 tablas críticas dentro de la ficha "Historia" de SIGGES.

### A. Tabla "Datos del Paciente" (Cabecera)
| Campo | Selector / Origen | Transformación |
| :--- | :--- | :--- |
| **RUT** | Input de Búsqueda | Normalización (Puntos y Guión) |
| **Edad** | Texto bajo el Nombre | Extracción de entero (ej. "45 Años" -> `45`) |
| **Fallecido** | Alerta Roja en Cabecera | **NUEVO:** Extracción de fecha `dd-mm-yyyy`. Si no hay fecha, "No". |

### B. Tabla IPD (Informe de Proceso Diagnóstico)
*Fuente de confirmación de patología.*
| Columna SIGGES | Campo Interno | Uso Forense |
| :--- | :--- | :--- |
| **Fecha Confirmación** | `f_ipd` | Determina la antigüedad del caso. |
| **Estado** | `e_ipd` | Busca "Sí", "Confirmado" para validar `Apto RE`. |
| **Diagnóstico** | `d_ipd` | Texto libre para `Caso en Contra`. |

### C. Tabla OA (Órdenes de Atención)
*Fuente de Habilitantes y Objetivos.*
| Columna SIGGES | Campo Interno | Uso Forense |
| :--- | :--- | :--- |
| **Fecha** | `f_oa` | Fecha del procedimiento. Vital para `Frecuencias`. |
| **Código** | `c_oa` | **CRÍTICO:** Se compara contra `objetivos` del JSON. |
| **Estado** | `e_oa` | "Otorgado" valida el cumplimiento. |

### D. Tabla SIC (Solicitud de Interconsulta)
*Fuente de derivaciones.*
| Columna SIGGES | Campo Interno | Uso Forense |
| :--- | :--- | :--- |
| **Fecha** | `f_sic` | Cronología de la derivación. |
| **Destino** | `d_sic` | Valida si el paciente fue enviado a nivel terciario. |

---

## 2. ESTRUCTURA DE SALIDA (EXCEL DINÁMICO)

El Excel final se construye en tiempo de ejecución. No hay plantilla fija.

### Grupo 1: Identificación (Estático)
- RUT
- Nombre
- Fecha Nómina
- Edad
- Fallecido (Fecha/No)
- Estado (Vigente/No Vigente)

### Grupo 2: Analítica Lógica (Dinámico)
*Se generan N columnas según `mission_config.json`.*

| Prefijo | Ejemplo | Contenido |
| :--- | :--- | :--- |
| **Obj** | `Obj 040101` | `12-05-2025 | 10-01-2025` (Fechas de cumplimiento) |
| **Hab** | `Hab 500210` | `15-08-2024` (Fecha del habilitante) |
| **Excl** | `Excl 800100` | Fecha si el paciente tiene una patología excluyente. |

### Grupo 3: Semáforos Lógicos (Calculado)
- **Hab Vi:** ¿Tiene habilitantes vigentes? (Sí/No)
- **Apto RE:** ¿Está confirmado clínicamente? (IPD/OA/APS)

---

## 3. PROTOCOLO DE CONSERVACIÓN DE DATOS
- **No-Persistencia:** Nozhgess no guarda base de datos local. Todo se procesa en RAM y se vuelca al Excel.
- **Anonimización:** Los logs de consola truncan el RUT (`12.3XX.XXX-K`) por seguridad.
- **Integridad:** Las fechas SIEMPRE se manejan como objetos `datetime` internamente y solo se convierten a string al escribir el Excel.

---
**© 2026 Nozhgess Data Science**
