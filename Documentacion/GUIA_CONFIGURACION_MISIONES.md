# ⚙️ GUÍA DE CONFIGURACIÓN DE MISIONES (JSON) v3.5.1
> **Meta:** Domine la arquitectura de configuración para crear misiones precisas.

---

## 1. El Nuevo Paradigma: "Lo que configuras es lo que obtienes"
En la versión 3.5.1, Nozhgess elimina las columnas "fantasma". El Excel de salida es un espejo directo de su archivo JSON.

### Ejemplo Práctico
Si su JSON dice:
```json
"objetivos": ["040101", "040102"]
```
El Excel tendrá **exactamente** dos columnas: `Obj 040101` y `Obj 040102`.
*Si borra "040102" del JSON, la columna desaparecerá del Excel automáticamente.*

---

## 2. Estructura del JSON de Misión
Ubicación: `Lista de Misiones/Su_Mision.json`

### Bloque A: Identidad
```json
{
  "nombre_mision": "Diabetes Mellitus Tipo 2",
  "version": "2.0",
  "autor": "Equipo GES"
}
```

### Bloque B: Lógica de Negocio (El Corazón)
Aquí define qué buscar. **Cada código aquí crea una columna.**
```json
{
  "objetivos": [
    "030104",  // Crea columna "Obj 030104"
    "030105"   // Crea columna "Obj 030105"
  ],
  "habilitantes": [
    "DIAB_T2_CIE10" // Crea columna "Hab DIAB_T2_CIE10"
  ],
  "excluyentes": [
    "DIAB_T1_CIE10" // Crea columna "Excl DIAB_T1_CIE10"
  ]
}
```

### Bloque C: Parámetros del Motor
Controlan la sensibilidad del robot.
```json
{
  "ventana_dias": 365,      // Cuánto mirar hacia atrás
  "max_anios": 10,          // Profundidad histórica máxima
  "revisar_futuros": false, // ¿Mirar prestaciones con fecha futura? (Error humano)
  
  // FLAGS DE ACTIVACIÓN (NUEVO)
  "require_oa": true,       // ¿Buscar en Tabla OA?
  "require_ipd": true,      // ¿Buscar en Tabla IPD?
  "active_frequencies": true // ¿Calcular periodicidad?
}
```

---

## 3. Configuración Avanzada de Frecuencias (V2)
Puede definir reglas complejas para auditar controles.

```json
"frecuencias": [
  {
    "code": "030104",
    "freq_qty": 1,
    "freq_type": "Mes",    // Opciones: "Mes", "Año"
    "periodicity": "Mensual"
  },
  {
    "code": "030105",
    "freq_qty": 2,
    "freq_type": "Año",
    "periodicity": "Anual"
  }
]
```
Esto generará columnas `Freq 030104` (Resultado: "Cumple/No Cumple") y `Period 030104` (Label: "Mensual").

---

## 4. Validaciones de Seguridad
Para evitar errores catastróficos, el sistema ignora configuraciones peligrosas:
- **Sin Objetivos:** Si la lista `objetivos` está vacía, la misión se aborta.
- **Códigos Vacíos:** Strings vacíos `""` son eliminados silenciosamente.
- **Tipos Incorrectos:** Si pone un número donde va un texto, el `Normalizador` intentará convertirlo. Si falla, lo descarta.

---
**© 2026 Nozhgess Configuration Team**
