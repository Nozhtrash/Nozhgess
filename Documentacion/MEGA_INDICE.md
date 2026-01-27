# 📚 MEGA ÍNDICE: Documentación Completa del Proyecto Nozhgess

> "La verdad os hará libres, pero primero os enfadará." - Filosofía de Documentación Nozhgess

Este índice conecta **TODA** la documentación del proyecto, desde la infraestructura crítica hasta las debilidades más vergonzosas.

## 🏗️ 1. Infraestructura y Core (`/Core`)
Aquí vive el motor. Si esto falla, nada funciona.
*   **[Iniciador.md](Core/Iniciador.md)**: Cómo arranca el script. El "Fontanero" de los imports.
*   **[Drivers y Navegador.md](Core/Drivers_y_Navegador.md)**: La capa que maneja Edge, Selenium y el Puerto 9222.
*   **[Configuración Global.md](Core/Configuracion_Global.md)**: Explicación de `Mision_Actual.py`. La única fuente de verdad.
*   **[Arquitectura Híbrida.md](Core/Arquitectura_Hibrida.md)**: Cómo la GUI moderna (`App/src`) habla con el código legado (`universal_compatibility.py`).

## 🧠 2. Lógica de Negocio (`/Logica`)
El cerebro médico y de decisión.
*   **[Motor de Revisión.md](Logica/Motor_de_Revision.md)**: **CRÍTICO**. Explica `Conexiones.py`, el orquestador principal. Cómo decide si un paciente aprueba o reprueba.
*   **[Selectores y XPaths.md](Logica/Selectores_y_XPaths.md)**: Mapa de los elementos de SIGGES. Vital para cuando cambien la web.
*   **[Mini Tabla y Datos.md](Logica/Mini_Tabla_y_Datos.md)**: La lógica (con inyección JS) para leer los casos del paciente.
*   **[Lógica Auxiliar.md](Logica/Logica_Auxiliar.md)**: Limpieza de textos, fechas y normalización.

## 🛠️ 3. Utilidades y Herramientas (`/Utilidades`)
Los engranajes que hacen que el motor gire suave.
*   **[Esperas y Tiempos.md](Utilidades/Esperas_y_Tiempos.md)**: Filosofía "Zero-Sleep" y diccionario de timeouts.
*   **[Gestión de Errores.md](Utilidades/Errores_y_Excepciones.md)**: Traductor de excepciones de Selenium a humano.
*   **[Terminal y Logs.md](Utilidades/Terminal_y_Logs.md)**: Sistema de colores y archivos de log.
*   **[Validaciones y Seguridad.md](Utilidades/Validaciones_y_Seguridad.md)**: Framework de validación estricta (RUT, Fechas, Elementos).
*   **[Reintentos y Resiliencia.md](Utilidades/Reintentos_y_Resiliencia.md)**: Patrones Enterprise (Circuit Breaker, Backoff) para estabilidad.
*   **[Debug y Diagnóstico.md](Utilidades/Debug_y_Diagnostico.md)**: Sistema de logging multinivel y profiling.
*   **[Reportes y Excel.md](Utilidades/Reportes_y_Excel.md)**: Generación de salidas con estilos profesionales.

## 🖥️ 4. Interfaz Gráfica (`/GUI`)
Lo que ve el usuario.
*   **[Interfaz Gráfica.md](GUI/Interfaz_Grafica.md)**: Arquitectura de la App CustomTkinter y advertencia sobre versiones duplicadas.

## 🚀 5. Arquitectura Moderna (`/Moderno`)
La nueva generación del código (`App/src`) que está reemplazando al Legacy.
*   **[Funciones Avanzadas.md](Moderno/Funciones_Avanzadas.md)**: Reportes automáticos, monitoreo en tiempo real y reintentos (SmartRetry).
*   **[Optimización Rendimiento.md](Moderno/Optimizacion_Rendimiento.md)**: Cómo manejamos Datasets de 500MB+ sin explotar la RAM.
*   **[Interfaz Mejorada.md](Moderno/Interfaz_Mejorada.md)**: La nueva GUI "Enhanced" con modo oscuro y tarjetas de estado.
*   **[Detector Archivos.md](Moderno/Detector_Archivos.md)**: Algoritmo heurístico para encontrar Excels perdidos.
*   **[Configuración Segura.md](Moderno/Configuracion_Segura.md)**: Sistema blindado de variables de entorno y backups.

## 💀 6. Transparencia y Honestidad (`/Transparencia`)
Lo que nadie quiere documentar pero es vital.
*   **[Debilidades Conocidas.md](Transparencia/Debilidades_Conocidas.md)**: Dónde se rompe el script. (Lectura obligatoria para devs).
*   **[Historial de Parches.md](Transparencia/Historial_Parches.md)**: Por qué el código es así. "War Stories".

## 🏛️ 6. Archivos Legados (`/Legacy`)
Documentación histórica rescatada de carpetas perdidas. Útil para arqueología de código.
*   **[ESTADO_FINAL.md](Legacy/ESTADO_FINAL.md)**: Estado del proyecto a Enero 2026.
*   **[ANALISIS_DATOS.md](Legacy/ANALISIS_DATOS.md)**: Referencia normativa GES 2025.
*   **[ROADMAP.md](Legacy/ROADMAP.md)**: Ideas futuras.

## 🧠 5. Meta-Documentación (`/Meta`)
Sobre cómo se escribió esta documentación.
*   **[ESTANDARES_DOCUMENTACION.md](Meta/ESTANDARES_DOCUMENTACION.md)**: Reglas de formato y honestidad exigidas.
*   **[ANATOMIA_DEL_SISTEMA.md](Meta/ANATOMIA_DEL_SISTEMA.md)**: **CRÍTICO**. La "Caja Negra" revelada. Timings exactos, XPaths y diagrama de flujo interno. Leer antes de tocar código.

## 💀 6. Transparencia y Honestidad (`/Transparencia`)
*Documentación generada automáticamente por Antigravity (Google DeepMind) el 27/01/2026.*
