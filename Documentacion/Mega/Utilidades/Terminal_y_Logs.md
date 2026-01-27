# Sistema de Terminal y Logging (`Terminal.py`)

## 📌 Propósito y Definición
Gestiona la salida visual (lo que ve el usuario en la ventana negra) y los archivos de log (lo que usamos para auditar).
Es la "Cara" del script.

## ⚙️ Mecánicas Visuales
*   **Colorama**: Usa colores ANSI para diferenciar Info (Azul), Éxito (Verde), Warning (Amarillo) y Error (Rojo).
*   **Resumen Compacto**: `resumen_paciente` imprime una "tarjeta" visual por cada paciente procesado.
    *   Diseño: Barras verticales `|` y emojis para separar datos densos.

## 🪵 Sistema de Logs (Archivos)
*   **Ruta**: `Z_Utilidades/Logs`.
*   **Rotación**: Mantiene solo los últimos 4 logs para no llenar el disco.
*   **Bug Conocido**: El código busca `Z_Utilidades` relativo a sí mismo. Si el script se mueve, el logging puede fallar y crear una carpeta `logs_fallback`.

## ⚠️ Debilidades y Puntos de Falla (Honestidad Brutal)
1.  **Spam en Consola**: Si `DEBUG_MODE` está activo en `Mision_Actual.py`, la consola se vuelve ilegible por la velocidad del texto.
2.  **Encoding Windows**: `safe_print` existe solo porque la consola cmd.exe de Windows a veces crashea con emojis (UnicodeEncodeError). Es un parche sucio pero necesario.
3.  **Dependencia Circular**: A veces `Terminal` importa `Configuracion` que importa `Terminal`. Python lo maneja mal.
