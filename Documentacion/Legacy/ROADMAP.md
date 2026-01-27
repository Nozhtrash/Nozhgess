# 🚀 NOZHGESS v.4 - ROADMAP COMPLETO

> **Objetivo**: Transformar Nozhgess de un script de revisión manual a un **Sistema Inteligente de Auditoría GES** alimentado por la normativa oficial 2025.

---

## 📊 ANÁLISIS DE FUENTES DE DATOS

### Excel Trazadora 2025 v.3.xlsx (FUENTE PRINCIPAL)

| Hoja | Registros | Contenido | Uso en v.4 |
|------|-----------|-----------|------------|
| **Arancel GES** | 1,047 | Códigos trazadora, familias, excluyentes, edades, periodicidad | Auto-generar misiones |
| **Canasta GES** | 12,445 | Prestaciones detalladas por problema de salud | Validar completitud |
| **Arancel NO GES** | Variable | Prestaciones PPV | Expandir a programas no-GES |
| **Eliminados** | Variable | Códigos descontinuados | Alertar obsoletos |

### Columnas Clave Identificadas (Arancel GES)

```
Código Familia, Familia, Trazadora, Glosa Trazadora,
Tipo Trazadora (Trazadora/Monitoreo), Edad, Sexo,
Nº Frecuencia, Periodicidad, Excluyentes, Regla ISFAM,
Precio 2025, Especialidad
```

### Problemas de Salud Detectados: 99 únicos

Ejemplos: Diabetes Mellitus Tipo 1/2, Cáncer Cervicouterino, Infarto Agudo, ERC 4-5, etc.

### Intervenciones Sanitarias: 8 tipos

- DIAGNÓSTICO
- TRATAMIENTO  
- SEGUIMIENTO
- TAMIZAJE
- DIAGNÓSTICO Y TRATAMIENTO
- REHABILITACIÓN
- ETAPIFICACIÓN
- CONFIRMACIÓN Y ETAPIFICACIÓN

---

## 🏗️ ARQUITECTURA PROPUESTA v.4

### Nuevos Módulos

```
Z_Utilidades/
├── Inteligencia/                    # 🧠 NUEVO - Núcleo IA
│   ├── __init__.py
│   ├── BaseConocimientoGES.py       # Carga y consulta Trazadora
│   ├── GeneradorMisiones.py         # Auto-genera misiones desde código PS
│   ├── ValidadorReglas.py           # Valida contra norma técnica
│   └── MotorAlertas.py              # Sistema de alertas inteligentes
│
├── Motor/                           # Existente - mejoras
│   ├── Formatos.py                  # + Normalización avanzada
│   └── ...
│
└── Mezclador/
    └── Conexiones.py                # Integra módulos Inteligencia
```

---

## 📋 FASES DE IMPLEMENTACIÓN

### FASE 1: Base de Conocimiento (Semana 1-2)

**Prioridad: CRÍTICA** | **Esfuerzo: Medio**

- [ ] Crear `BaseConocimientoGES.py`
  - Carga Excel Trazadora al iniciar
  - Métodos de consulta por código problema
  - Cache en memoria para velocidad
  
- [ ] Funciones principales:

  ```python
  def obtener_problema(codigo: int) -> Dict
  def obtener_trazadoras(codigo_problema: int) -> List[Dict]
  def obtener_excluyentes(codigo_trazadora: str) -> List[str]
  def obtener_reglas_edad(codigo_trazadora: str) -> Tuple[int, int]
  def obtener_periodicidad(codigo_trazadora: str) -> str
  ```

### FASE 2: Generador de Misiones (Semana 2-3)

**Prioridad: ALTA** | **Esfuerzo: Medio**

- [ ] Crear `GeneradorMisiones.py`
  - Input: Código de problema de salud (1-99)
  - Output: Diccionario de misión completo
  
- [ ] Auto-genera:
  - Keywords desde nombre del problema
  - Códigos habilitantes desde trazadoras
  - Excluyentes desde columna oficial
  - Rangos de edad
  - Periodicidad esperada
  - Familia y especialidad

```python
# ANTES (manual):
MISSIONS = [{
    "nombre": "Diabetes Mellitus 1",
    "keywords": ["diabetes mellitus I", ...],  # Manual
    "habilitantes": ["3102001", "3102002"],    # Manual
    ...
}]

# DESPUÉS (automático):
mision = GeneradorMisiones.crear_desde_codigo(8)  # Código DM1
# Genera todo automáticamente desde la Trazadora
```

### FASE 3: Validador de Reglas (Semana 3-4)

**Prioridad: ALTA** | **Esfuerzo: Alto**

- [ ] Crear `ValidadorReglas.py`
  - Valida cumplimiento de norma técnica
  - Detecta anomalías

- [ ] Validaciones implementar:

  ```python
  def validar_edad(paciente_edad: int, codigo: str) -> Tuple[bool, str]
  def validar_sexo(paciente_sexo: str, codigo: str) -> Tuple[bool, str]
  def validar_periodicidad(fechas: List, esperada: str) -> Tuple[bool, str]
  def validar_excluyentes(prestaciones: List, codigo: str) -> List[str]
  def validar_regla_isfam(caso: Dict, codigo: str) -> Tuple[bool, str]
  ```

### FASE 4: Motor de Alertas (Semana 4-5)

**Prioridad: MEDIA** | **Esfuerzo: Medio**

- [ ] Crear `MotorAlertas.py`
  - Genera alertas contextuales
  - Categoriza por severidad

- [ ] Tipos de alerta:

  | Nivel | Descripción | Ejemplo |
  |-------|-------------|---------|
  | 🔴 CRÍTICO | Bloquea procesamiento | Código obsoleto |
  | 🟠 ADVERTENCIA | Requiere revisión | Edad fuera de rango |
  | 🟡 INFO | Sugerencia | Próximo a vencer periodicidad |
  | 🟢 OK | Cumple norma | Prestación en tiempo |

### FASE 5: Nuevas Columnas Output (Semana 5-6)

**Prioridad: MEDIA** | **Esfuerzo: Bajo**

- [ ] Agregar columnas inteligentes:

| Nueva Columna | Descripción |
|---------------|-------------|
| `Cumplimiento %` | Porcentaje de canasta cumplida |
| `Alerta` | Alertas detectadas |
| `Sugerencia` | Próximas acciones recomendadas |
| `Periodicidad OK` | ✅/❌ cumple frecuencia esperada |
| `Edad Válida` | ✅/❌ dentro del rango |
| `Código Obsoleto` | Lista de códigos eliminados usados |

---

## 🔧 CAMBIOS EN ARCHIVOS EXISTENTES

### `Mision_Actual.py`

```python
# NUEVO: Modo automático
MODO_AUTOMATICO = True
CODIGO_PROBLEMA_SALUD = 8  # Solo esto necesita el usuario

# El sistema auto-genera el resto desde la Trazadora
```

### `Conexiones.py`

```python
# NUEVO: Integración con inteligencia
from Z_Utilidades.Inteligencia import BaseConocimientoGES, ValidadorReglas

# En analizar_mision():
alertas = ValidadorReglas.validar_todo(caso, prestaciones, codigo_trazadora)
res["Alerta"] = " | ".join(alertas)
```

---

## 📈 BENEFICIOS ESPERADOS

| Métrica | Actual | v.4 |
|---------|--------|-----|
| Tiempo configurar misión | 15-30 min | < 1 min |
| Errores por config manual | Frecuentes | Eliminados |
| Cobertura validaciones | ~40% | 95%+ |
| Alertas proactivas | 0 | Automáticas |
| Actualización normativa | Manual | Semi-auto |

---

## 📁 ARCHIVOS A CREAR

```
Nozhgess v.4/
├── ROADMAP.md                    # Este archivo
├── ANALISIS_DATOS.md             # Detalle del análisis
├── ARQUITECTURA.md               # Diseño técnico detallado
├── GUIA_IMPLEMENTACION.md        # Paso a paso
├── prototipos/
│   ├── BaseConocimientoGES.py    # Prototipo funcional
│   └── GeneradorMisiones.py      # Prototipo funcional
└── tests/
    └── test_base_conocimiento.py # Tests unitarios
```

---

## ⏱️ CRONOGRAMA SUGERIDO

```
Semana 1-2: Fase 1 (Base Conocimiento)     ████████░░
Semana 2-3: Fase 2 (Generador Misiones)    ░░████████
Semana 3-4: Fase 3 (Validador Reglas)      ░░░░██████
Semana 4-5: Fase 4 (Motor Alertas)         ░░░░░░████
Semana 5-6: Fase 5 (Columnas + Integración)░░░░░░░░██
```

**Total estimado: 6 semanas** para implementación completa.

---

## 🎯 SIGUIENTE PASO INMEDIATO

1. Revisar y aprobar este roadmap
2. Comenzar con `BaseConocimientoGES.py` (núcleo de todo)
3. Crear tests básicos
4. Iterar

---

*Generado: 2026-01-19 | Nozhgess v.4 Planning*
