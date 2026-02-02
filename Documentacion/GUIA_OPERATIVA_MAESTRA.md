# 📘 GUÍA OPERATIVA MAESTRA NOZHGESS v2.0

> **Destinatario:** Usuarios Operadores, Administrativos y Gestores de SIGGES.
> **Propósito:** Manual de vuelo paso a paso.
> **Prerrequisito:** Tener instalado Microsoft Edge y Excel.

---

# 1. INTRODUCCIÓN

Bienvenido a **Nozhgess**, su asistente automatizado para la revisión de garantías explícitas (GES). Esta herramienta no es mágica; es un robot de alta precisión que navega por SIGGES igual que usted, pero más rápido y sin cansarse.

**¿Qué hace y qué NO hace?**
*   ✅ **Hace:** Entra a SIGGES, busca pacientes por RUT, descarga historial, analiza fechas y genera un Excel coloreado.
*   ❌ **NO Hace:** Tomar decisiones médicas, pasar por alto errores de conexión o inventar datos que no existen.

---

# 2. PREPARACIÓN DEL VUELO (ANTES DE INICIAR)

## 2.1. El Archivo "Misión" (Excel de Entrada)
El robot necesita coordenadas. Usted debe proveer un archivo Excel con los pacientes a revisar.
*   **Requisito 1:** El archivo debe estar cerrado. Si lo tiene abierto, el robot fallará.
*   **Requisito 2:** Debe tener columnas con encabezados claros (RUT, Nombre).
*   **Tip:** No use espacios ni caracteres raros en el nombre del archivo. `ListaPacientes.xlsx` es mejor que `Lista Final Final (1).xlsx`.

## 2.2. Reinicio de Entorno
Para asegurar un viaje sin turbulencias:
1.  Cierre todas las ventanas de Microsoft Edge.
2.  Asegúrese de tener conexión a internet estable.

---

# 3. EJECUCIÓN PASO A PASO

## Paso 1: Encendido de Motores (Launcher)
Haga doble click en el archivo `Nozhgess.pyw` (icono de la serpiente azul).
*   Se abrirá una ventana negra futurista: Es la **Consola de Control**.

## Paso 2: Conexión con SIGGES (El Puente 9222)
En el panel izquierdo, verá un botón que dice **"Iniciar Edge (Debug)"**.
1.  Presiónelo **UNA VEZ**.
2.  Espere 5 segundos.
3.  Se abrirá una ventana de Edge blanca o vacía. **NO LA CIERRE.**
4.  En esa ventana, navegue manualmente a `www.sigges.cl` e inicie sesión con su clave.
5.  **IMPORTANTE:** Deje la sesión iniciada en la pantalla de bienvenida ("Seleccione Unidad"). No avance más.

## Paso 3: Selección de Misión
En el menú desplegable de la aplicación (arriba a la derecha), seleccione qué tipo de revisión hará (ej: "Diabetes I", "Hipertensión").
*   *Nota:* Esto carga las reglas específicas (qué códigos buscar, qué plazos aplicar).

## Paso 4: Cargar Combustible (Excel)
Presione el botón **"Cargar Excel"** y seleccione su archivo de pacientes.

## Paso 5: Despegue
Presione el botón **"▶ EJECUTAR MISION"**.
*   El robot tomará el control del mouse y teclado dentro de SIGGES.
*   **NO ITERRUMPA** el proceso moviendo el mouse bruscamente sobre la ventana de Edge. Puede minimizarla, pero es mejor dejarla visible en un segundo monitor.

---

# 4. INTERPRETANDO EL SEMÁFORO DE LA CONSOLA

La pantalla negra le hablará con emojis. aprenda su idioma:

| Señal | Significado | Acción Requerida |
| :--- | :--- | :--- |
| 🔄 **Spinner Detectado** | El robot está esperando que SIGGES cargue. | Paciencia. No toque nada. |
| ⚠️ **Reintentando...** | Algo falló (ej: click fallido), intentará de nuevo. | Observar. Si falla 3 veces, saltará al siguiente. |
| ❌ **Error Fatal** | Se cayó Internet o se cerró Edge. | Detener, cerrar todo y volver al Paso 2. |
| 💾 **Excel Guardado** | Misión cumplida exitosamente. | Abra la carpeta de salida y celebre. |

---

# 5. ANATOMÍA DEL EXCEL FINAL (EL RESULTADO)

El reporte que entrega Nozhgess es su mapa táctico. Cada color tiene un significado estricto.

## 🔵 Zona Azul: Identificación
Datos duros del paciente.
*   **RUT, Nombre, Edad:** Extraídos directamente de SIGGES.

## 🟢 Zona Verde: Estado del Caso
*   **Caso:** El nombre de la enfermedad (ej: "Diabetes Mellitus Tipo 2").
*   **Estado:** Si dice **"Vigente"** (en texto rojo dentro del Excel), es prioridad. Si dice **"Cerrado"**, está OK.
*   **Apertura:** Fecha de inicio del caso.

## 🟤 Zona Café: Tiempos
Calculadoras automáticas.
*   **Mensual:** Cuántos meses han pasado desde la apertura. Vital para saber si está atrasado.
*   **Periodicidad:** Regla aplicada (ej: "Cada 3 meses").

## 🌺 Zona Rosada: Inteligencia Artificial (Lógica)
Aquí es donde el robot "piensa".
*   **Apto SE (Seguimiento):** El robot sugiere: "Este paciente debería estar en seguimiento".
*   **Apto RE (Revisión):** El robot sugiere: "Hay confirmación diagnóstica (IPD), revíselo".

## 🔴 Zona Roja: Hallazgos Críticos (Habilitantes)
Si aparece una columna roja con una fecha (ej: "FONDO DE OJO - 12/05/2025"), significa que el robot encontró ese examen específico en el historial.

---

# 6. SOLUCIÓN DE PROBLEMAS COMUNES (FAQ)

### P: "El robot dice 'Conectado' pero no se mueve."
**R:** Probablemente la ventana de Edge se "durmió". Haga click dentro de la ventana de Edge para despertarla y vuelva a dar ejecutar.

### P: "Me sale error 'Session Not Created'."
**R:** Su Edge se actualizó atomáticamente y el driver quedó viejo. Avise a soporte técnico para actualizar el archivo `msedgedriver.exe`.

### P: "El Excel sale vacío o con datos raros."
**R:** SIGGES cambió su diseño. El robot necesita una actualización de "Mapa" (`locators.py`). Detenga el uso y reporte.

---
**Recuerde:** Usted es el piloto, Nozhgess es el copiloto. Siempre verifique los casos críticos manualmente.
