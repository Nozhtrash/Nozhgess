# ⚙️ GUIA DE CONFIGURACIÓN DE MISIONES (JSON)
> **Versión:** 1.0 (Feb 2026)
> **Archivo:** `App/config/mission_config.json`

Esta guía detalla el significado de cada "llave" en el cerebro de Nozhgess. Modificar estas variables altera el comportamiento clínico del robot.

---

# 1. ESQUEMA BASE

Cada misión en el JSON debe seguir esta estructura mínima:

```json
{
  "nombre_mision": "Diabetes Tipo 2",
  "indices": { "rut": 1, "nombre": 3, "familia": 2 },
  "habilitantes": ["5002101", "5002102"],
  "excluyentes": ["5001101"],
  "require_ipd": true,
  "max_habilitantes": 1
}
```

---

# 2. DICCIONARIO DE VARIABLES

### 📊 Estructura de Entrada (`indices`)
Define qué columnas del Excel que usted sube contienen qué datos.
- **`rut`**: Índice de columna (Base 0 o 1 según implementación). 
- **`nombre`**: Nombre completo del paciente.
- **`fecha`**: Fecha de la nómina (para calcular vigencia).

### 🩺 Lógica Clínica
- **`habilitantes`**: Lista de códigos de prestaciones (OA) que activan la alerta roja.
- **`excluyentes`**: Códigos que, si se encuentran, marcan al paciente como "No Apto" para esta misión.
- **`keywords_mision`**: Términos que el robot busca en la lista de casos de SIGGES para saber a qué cartola entrar.
- **`keywords_contra`**: Términos para detectar el "Caso en Contra". Si encuentra esto, activa la lógica de extracción divergente.

### 📜 Banderas de Activación (`require_...`)
- **`require_ipd`**: Si es `true`, el robot buscará la fecha de confirmación diagnóstica.
- **`require_oa`**: Si es `true`, el robot leerá la tabla de Órdenes de Atención.
- **`require_sic`**: Activa la búsqueda de interconsultas.
- **`folio_vih`**: (Opt-in) Solo para misiones de VIH. Busca la columna Folio específica.

### ⚖️ Límites y Filtros
- **`max_habilitantes`**: Límite de exámenes rojos a reportar. Si hay 10 y el límite es 1, solo pondrá el más reciente.
- **`anios_codigo`**: Mapeo para inyección por edad. 
    *   *Ejemplo:* `{"0": "5002101", "15": "5003101"}` -> A los 15 años cambia el código clínico.

---

# 3. EJEMPLO DE CONFIGURACIÓN AVANZADA (VIH)

```json
{
  "nombre_mision": "VIH Operativo",
  "keywords_mision": ["VIH", "Inmunosupresión"],
  "require_ipd": true,
  "require_oa": true,
  "folio_vih": true,
  "indices": { "rut": 0, "nombre": 1 },
  "habilitantes": ["0801103", "0801104"]
}
```

---

# 4. SOLUCIÓN DE ERRORES (CONFIG)

- **Problema:** "El robot entra a casos que no son".
  - **Fix:** Refinar `keywords_mision`. Sea más específico.
- **Problema:** "Me faltan columnas en el Excel".
  - **Fix:** Verifique que las banderas `require_...` estén en `true`. Nozhgess oculta columnas inactivas para ahorrar espacio.

---

**© 2026 Nozhgess Config Lab**
*"Un JSON bien configurado es un reporte sin errores."*
