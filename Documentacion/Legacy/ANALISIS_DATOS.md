# 📊 ANÁLISIS DE DATOS - Fuentes Normativas GES 2025

> Análisis detallado de la documentación disponible para alimentar la inteligencia de Nozhgess v.4

---

## 📁 INVENTARIO DE FUENTES

| Archivo | Tipo | Tamaño | Estado Extracción |
|---------|------|--------|-------------------|
| `Trazadora 2025 v.3.xlsx` | Excel | 715 KB | ✅ **COMPLETO** |
| `DECRETO 29 del 2025.pdf` | PDF | 33.7 MB | ⚠️ Imagen escaneada |
| `DECRETO EXENTO N° 57 SSP 2025.pdf` | PDF | 1.2 MB | ⚠️ Imagen escaneada |
| `NORMA TECNICA DECRETO EXENTO N 57 SSP 2025.pdf` | PDF | 34.2 MB | ⚠️ Imagen escaneada |

> **Nota**: Los PDFs son documentos escaneados como imágenes, requieren OCR para extracción.
> El Excel contiene toda la información estructurada necesaria para la implementación inicial.

---

## 📗 EXCEL: TRAZADORA 2025 V.3

### Hoja 1: ARANCEL GES (Fuente Principal)

**Total registros**: 1,047 filas

#### Estructura de Columnas

| # | Columna | Descripción | Uso en Nozhgess |
|---|---------|-------------|-----------------|
| 0 | `Fecha inicio` | Vigencia desde | Validar vigencia |
| 1 | `Fecha término` | Vigencia hasta | Validar vigencia |
| 2 | `Cód. Problema de Salud` | 1-99 (identificador único) | **KEY para misiones** |
| 3 | `Problema de Salud` | Nombre completo | Keywords automáticos |
| 4 | `Sub-problema (rama)` | Subcategoría | Filtros avanzados |
| 5 | `Intervención Sanitaria` | Tipo intervención | Categorización |
| 6 | `Código Familia` | ID familia prestaciones | Agrupación |
| 7 | `Familia` | Nombre familia | Descripción |
| 8 | `Trazadora` | **Código prestación** | **Habilitantes/Objetivos** |
| 9 | `Homologado` | Código homologación | Mapeo alternativo |
| 10 | `Glosa Trazadora (PO)` | Descripción prestación | Display usuario |
| 11 | `Tipo Trazadora` | Trazadora/Monitoreo | Clasificación |
| 12 | `Edad` | Restricción edad | **Validación edad** |
| 13 | `Sexo` | Restricción sexo | **Validación sexo** |
| 14 | `Nº de Frecuencia` | Cantidad esperada | Conteo |
| 15 | `Periodicidad Frecuencia` | Mensual/Año/Vida | **Validación frecuencia** |
| 16 | `Periocidad Registro` | Cuándo registrar | Alertas timing |
| 17 | `Canasta` | Pertenencia canasta | Agrupación |
| 18 | `Excluyentes` | **Códigos excluyentes** | **Auto-excluyentes** |
| 19 | `Regla ISFAM` | Regla interconsulta | Validación ISFAM |
| 20 | `Clasificación` | Clasificación interna | Metadata |
| 21 | `Precio 2025` | Valor en pesos | Reportes |
| 22 | `Archivo` | Referencia archivo | Trazabilidad |
| 23 | `Comentario(s)` | Notas adicionales | Info extra |
| 24 | `Unidad` | Unidad medida | Formato |
| 25 | `Especialidad` | Código especialidad | **Auto-especialidad** |
| 26 | `Especialidad (CM)` | Especialidad CM | Alternativo |

#### Problemas de Salud Identificados (99 únicos)

```
1. ENFERMEDAD RENAL CRÓNICA ETAPA 4 Y 5
2. CARDIOPATÍAS CONGÉNITAS OPERABLES
3. CÁNCER CERVICOUTERINO
4. ALIVIO DEL DOLOR Y CUIDADOS PALIATIVOS POR CÁNCER
5. INFARTO AGUDO DEL MIOCARDIO
6. DIABETES MELLITUS TIPO 1
7. DIABETES MELLITUS TIPO 2
8. CÁNCER DE MAMA
9. DISRAFIAS ESPINALES
10. TRATAMIENTO QUIRÚRGICO DE ESCOLIOSIS EN MENORES DE 25 AÑOS
11. TRATAMIENTO QUIRÚRGICO DE CATARATAS
... (89 más)
```

#### Intervenciones Sanitarias (8 tipos)

| Intervención | Descripción |
|--------------|-------------|
| DIAGNÓSTICO | Confirmación diagnóstica |
| TRATAMIENTO | Intervenciones terapéuticas |
| SEGUIMIENTO | Control posterior |
| TAMIZAJE | Screening poblacional |
| DIAGNÓSTICO Y TRATAMIENTO | Combinado |
| REHABILITACIÓN | Recuperación funcional |
| ETAPIFICACIÓN | Clasificación estadio |
| CONFIRMACIÓN Y ETAPIFICACIÓN | Combinado |

#### Ejemplo: Diabetes Mellitus Tipo 1

| Código Familia | Familia | Trazadora | Glosa | Excluyentes | Periodicidad |
|----------------|---------|-----------|-------|-------------|--------------|
| -47 | CONFIRMACION PACIENTES CON DM TIPO 1 | 109001 | CONSULTA TELEMEDICINA | 0.3102 | Año |
| -47 | CONFIRMACION PACIENTES CON DM TIPO 1 | 302046 | Gases y equilibrio ácido base | ,3102003,0109001 | Año |
| -47 | CONFIRMACION PACIENTES CON DM TIPO 1 | 3102003 | CONFIRMACION DG. PCTES. NUEVOS | 0.0109 | Año |
| -86 | EVALUACION INICIAL HOSPITALIZADO | 3102101 | Sin cetoacidosis | ,3102003,3102102 | Año |
| -85 | EVALUACION INICIAL HOSPITALIZADO | 3102102 | Con cetoacidosis | ,3102003,3102101 | Año |
| -215 | TRATAMIENTO 1° AÑO | 3102001 | Tratamiento incluye descompensaciones | 0.3102 | Año |
| -217 | TRATAMIENTO 2° AÑO+ | 3102002 | Control y tratamiento mensual | 0.3102 | Año |

---

### Hoja 2: CANASTA GES

**Total registros**: 12,445 filas

#### Estructura

| Columna | Descripción |
|---------|-------------|
| `Nº` | Código problema de salud |
| `Problema de salud` | Nombre |
| `Intervención sanitaria` | Tipo |
| `Prestación o grupo de prestaciones` | Agrupación |
| `Codigo` | **Código prestación específica** |
| `Glosa` | Descripción detallada |
| `Observacion` | Notas |

#### Uso en Nozhgess v.4

Esta hoja permite:

- ✅ Validar que una prestación pertenece a la canasta de un problema
- ✅ Calcular % de completitud de canasta
- ✅ Detectar prestaciones fuera de canasta
- ✅ Sugerir prestaciones faltantes

---

### Hoja 3: ARANCEL NO GES

**Contenido**: Prestaciones de Programa de Prestaciones Valoradas (PPV)

| Columna | Descripción |
|---------|-------------|
| `PROGRAMA` | Nombre programa |
| `SUB-PROGRAMA` | Subcategoría |
| `Código Familia` | ID familia |
| `Familia` | Nombre familia |
| `Trazadora` | Código prestación |
| ... | Similar a Arancel GES |

#### Uso Potencial

- Expandir Nozhgess a programas NO GES
- Validar prestaciones PPV
- Futuro: modo híbrido GES + NO GES

---

### Hoja 4: ELIMINADOS

**Contenido**: Códigos descontinuados en 2025

#### Uso en Nozhgess v.4

- ⚠️ Alertar si paciente tiene prestación con código obsoleto
- 🔄 Sugerir código de reemplazo si existe
- 📊 Detectar inconsistencias históricas

---

## 📄 PDFs: NORMA TÉCNICA Y DECRETOS

### Estado Actual

Los PDFs son **documentos escaneados como imágenes**, lo que significa:

- No se puede extraer texto directamente
- Requieren OCR (Reconocimiento Óptico de Caracteres)
- El proceso de OCR es lento y propenso a errores

### Contenido Esperado (según nombres)

| PDF | Contenido Probable | Páginas |
|-----|-------------------|---------|
| DECRETO 29 del 2025 | Marco legal GES 2025 | 288 |
| DECRETO EXENTO N° 57 | Resolución específica SSP | 3 |
| NORMA TÉCNICA DECRETO 57 | Detalle técnico implementación | 91 |

### Opción para Futuro

Para extraer información de los PDFs:

1. **OCR con Tesseract**: `pip install pytesseract pdf2image`
2. **Servicio Cloud**: Google Vision API, AWS Textract
3. **Manual**: Transcribir secciones clave manualmente

> **Recomendación**: Por ahora, el Excel Trazadora contiene suficiente información estructurada.
> Los PDFs se pueden incorporar en una fase posterior cuando se requiera validación legal específica.

---

## 🔑 CONCLUSIONES PARA IMPLEMENTACIÓN

### Datos Disponibles Inmediatamente

| Funcionalidad | Fuente | Viabilidad |
|---------------|--------|------------|
| Auto-generar keywords | Excel col. "Problema de Salud" | ✅ Inmediata |
| Auto-detectar habilitantes | Excel col. "Trazadora" | ✅ Inmediata |
| Auto-detectar excluyentes | Excel col. "Excluyentes" | ✅ Inmediata |
| Validar rangos de edad | Excel col. "Edad" | ✅ Inmediata |
| Validar periodicidad | Excel col. "Periodicidad Frecuencia" | ✅ Inmediata |
| Detectar códigos obsoletos | Excel hoja "Eliminados" | ✅ Inmediata |
| Validar completitud canasta | Excel hoja "Canasta GES" | ✅ Inmediata |
| Obtener especialidad | Excel col. "Especialidad" | ✅ Inmediata |

### Datos Pendientes (requieren OCR de PDFs)

| Funcionalidad | Fuente | Viabilidad |
|---------------|--------|------------|
| Reglas legales específicas | DECRETO 29 | ⏳ Fase posterior |
| Algoritmos clínicos | NORMA TÉCNICA | ⏳ Fase posterior |
| Tiempos de garantía GES | PDFs varios | ⏳ Fase posterior |

---

*Documento generado: 2026-01-19 | Nozhgess v.4 - Análisis de Datos*
