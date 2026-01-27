# Interfaz Gráfica (`App/src/gui`)

## 📌 Propósito y Definición
La GUI es el "Control de Misión".
Desarrollada en **CustomTkinter** (un wrapper moderno de Tkinter), permite al usuario configurar y lanzar misiones sin tocar código.

## ⚙️ Arquitectura Modular
A diferencia de los scripts monolíticos antiguos, la GUI está dividida en módulos:
*   `app.py`: El punto de entrada principal (invocado por `Nozhgess.pyw`).
*   `views/`: Cada pestaña ("Misiones", "Runner", "Settings") es una clase separada.
*   `theme.py`: Diccionario centralizado de colores (Modo Oscuro/Claro).

## ⚠️ "Infierno de Versiones" (Honestidad Brutal)
En la carpeta `App/src/gui` encontrarás archivos zombies:
*   `enhanced_app.py`
*   `final_app.py`
*   `ultra_optimized_app.py`
**IGNÓRALOS**. Son reliquias de intentos de optimización pasados.
El único archivo que importa es **`app.py`**. Si editas `super_final_app.py`, no cambiará nada en el ejecutable real.

## 🔄 Flujo de Datos
1.  **Input**: Usuario escribe keywords o selecciona misión en la GUI.
2.  **Persistencia**: Al dar click en "Guardar", se escribe un JSON en `user_settings.json` o `mission_config.json`.
3.  **Lanzamiento**: Al dar click en "Usar Ahora", la GUI genera dinámicamente el archivo `Mision_Actual.py` (sobrescribiéndolo) y luego lanza el subproceso del script.
    *   *Riesgo*: Si la GUI falla al generar `Mision_Actual.py` (ej: problema de permisos), el script correrá con la misión *anterior* sin avisar.

## 🎨 Temas y Estilos
CustomTkinter usa un sistema de pesos. Nozhgess fuerza el "Dark Mode" por defecto, pero respeta la configuración del sistema si se cambia en `theme.py`.
