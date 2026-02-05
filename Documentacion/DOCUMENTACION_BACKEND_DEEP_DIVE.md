# 🛠️ DEEP DIVE BACKEND: EL SISTEMA NERVIOSO v3.5.0
> **Audiencia:** Desarrolladores de Sistemas, Expertos en Automatización y Soporte Nivel 3.
> **Propósito:** Documentación forense para la reparación, expansión y auditoría del motor "Nuclear".

---

# 1. ANATOMÍA DEL "HOOK" (SESSION PARASITISM)

Nozhgess no es un bot que abre un navegador limpio; es un **parásito de sesión**. Se conecta a una instancia de Edge ya abierta y autenticada.

### 1.1. El Protocolo: Chrome DevTools Protocol (CDP)
El motor utiliza el puerto `9222` para enviar comandos JSON directamente al motor Chromium de Edge.
- **Control Remoto:** Esto permite que el robot "vea" lo que el usuario ve, heredando cookies, tokens de seguridad y certificados NTML/Windows.

### 1.2. El Puente PowerShell (`Iniciador Web.ps1`)
Este script es el "Gatillo". Sin él, Nozhgess es un cuerpo sin ojos.
- **Flags Críticos:**
  - `--remote-debugging-port=9222`: Abre el socket de escucha.
  - `--user-data-dir="C:\Selenium\EdgeProfile"`: Aísla la sesión para evitar corromper el historial personal del usuario.
  - `--start-maximized`: Asegura que los elementos HTML no se oculten por responsividad (Media Queries).

---

# 2. ORQUESTACIÓN DE `Conexiones.py`

Este archivo es el **Cerebro Operativo**. No solo navega, sino que toma decisiones en milisegundos.

### 2.1. El Pipeline de Extracción
Cada paciente sigue un ciclo de lectura de sub-tablas:

1.  **IPD (Informes Diagnósticos):**
    - Busca la confirmación del diagnóstico.
    - *Lógica:* Si la columna "Confirmado" es "SÍ", captura la fecha para el **Apto RE**.
2.  **OA (Órdenes de Atención):**
    - Rastrea todos los exámenes y procedimientos.
    - *Lógica:* Compara el código de la web contra la lista `habilitantes` del JSON.
3.  **APS (Atención Primaria):**
    - Verifica si hay atenciones en consultorios.
4.  **SIC (Interconsultas):**
    - Detecta si el paciente fue derivado a un especialista (Vital para el **Apto SE**).

### 2.2. Manejo de la "Verdad Clínica"
- **Normalización de Nombres:** Limpia espacios dobles y caracteres invisibles que SIGGES a veces inserta.
- **Detección de Casos Activos:** `seleccionar_caso_inteligente` utiliza un algoritmo de puntaje (EsActivo * 10^10 + Timestamp) para asegurar que siempre trabajamos sobre el caso que el hospital tiene abierto hoy.

---

# 3. GESTIÓN DE FALLOS Y FAIL-SAFE

### 3.1. Detección Fatal (`es_conexion_fatal`)
Capture de excepciones binarias. Si el sistema detecta:
- `Connection refused`: El usuario cerró Edge.
- `No such window`: Se cerró la pestaña de SIGGES.
- `Session not created`: El Driver (`msedgedriver.exe`) es incompatible con la versión de Edge.

### 3.2. Lógica de Reintentos (Anti-Lag)
- **Wait For Spinner:** El motor monitorea el elemento `div.loading-spinner`. Si aparece, el robot "presiona el freno" automáticamente.
- **Reintento de Click:** Si un click falla por un overlay (ej. un tooltip que se cruzó), el sistema intenta un **Click de JavaScript de Fuerza Bruta** (`arguments[0].click()`).

---

# 4. MAPA DE DEPENDENCIAS Y CRITICAL IMPORTS

Si planea refactorizar, respete este árbol de dependencias para evitar errores de importación circular:

```text
Nozhgess.pyw (Root)
└── App.src.gui.app (Container)
    └── App.src.gui.views.runner (Threading Controller)
        └── Utilidades.Mezclador.Conexiones (Business Logic)
            ├── App.src.core.Driver (Selenium Engine)
            ├── App.src.core.Analisis_Misiones (Validation Engine)
            └── App.src.core.Formatos (Data Sanitization)
```

---

# 5. TROUBLESHOOTING DE BAJO NIVEL (N3)

### 🚨 "Stale Element Reference Exception"
- **Diagnóstico:** El robot tiene la dirección de un botón, pero la página se refrescó y esa dirección ya no sirve.
- **Solución:** El motor `core.py` implementa `_invalidar_cache_estado()`. Verifique que se llame antes de cada interacción importante en `Conexiones.py`.

### 🚨 El Excel se genera pero las fechas salen como números
- **Diagnóstico:** Formato de celda de Excel inválido.
- **Solución:** `Excel_Revision.py` debe aplicar la propiedad `.number_format = 'dd/mm/yyyy'` explícitamente a las columnas clínicas.

---

**© 2026 Nozhgess Engineering Team**
*"La robustez es el único estándar aceptable."*
