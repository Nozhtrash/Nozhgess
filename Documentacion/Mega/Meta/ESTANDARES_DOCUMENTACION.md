# Estándares de Documentación - Nozhgess

## 📌 Principios Fundamentales
Toda documentación en este proyecto debe seguir los principios de **"Honestidad Brutal"** y **"Utilidad Técnica"**.
No queremos "lorem ipsum" corporativo. Queremos manuales de trinchera.

## 📝 Formato Requerido por Archivo (`.md`)

### 1. Encabezado
Debe indicar claramente qué módulo se está documentando y su ruta original.
```markdown
# [Nombre del Módulo] (`Ruta/Al/Archivo.py`)
```

### 2. Propósito y Definición
¿Para qué sirve esto? ¿Por qué existe?
*   Explicar el "Dolor" que resuelve (ej: "Sin esto, el script se cae si falla internet").
*   Evitar tecnicismos vacíos.

### 3. Lógica y Mecánica (Cómo funciona)
*   Explicar el flujo paso a paso.
*   Mencionar funciones clave.
*   **Math & Logic**: Si hay fórmulas (ej: puntaje de priorización), explicarlas.

### 4. Debilidades (Weaknesses & Bugs)
*   **Sección Crítica**: Admite qué partes son frágiles.
*   Ej: "Este módulo falla si el usuario tiene el Excel abierto".
*   Esto ayuda al futuro desarrollador a saber dónde pisar con cuidado.

### 5. Configuración (Si aplica)
*   Qué variables `CONSTANTES` afectan este módulo.

## 🎨 Estilo Visual
*   Usar emojis para escanear rápido (📌, ⚙️, 🛡️, ⚠️).
*   Usar `code blocks` para ejemplos de código.
*   Usar **negritas** para conceptos clave.

## 🚫 Lo que NO hacemos
*   Documentar getters/setters obvios.
*   Ocultar 'hacks' o parches feos. (Al revés, ¡documentalos con orgullo para poder arreglarlos luego!).
