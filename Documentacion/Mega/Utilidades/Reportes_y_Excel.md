# Generación de Reportes Excel (`Excel_Revision.py`)

## 📌 Propósito y Definición
El entregable final. Convierte los diccionarios de datos Python en un archivo `.xlsx` estéticamente "gerencial".

## 🎨 Paleta de Colores Semántica
No usa colores al azar. Cada grupo de columnas tiene un significado visual (`COLORS` map):
*   **Verde**: Datos básicos (RUT, Nombre).
*   **Amarillo**: Clasificación (Familia, Especialidad).
*   **Rojo/Naranja**: Alertas críticas (IPD, Excluyentes).
*   **Morado**: Estados del caso.

## ⚙️ Características Técnicas (`openpyxl`)
1.  **Estilos Automáticos**: Detecta el nombre de la columna (ej: "Fecha IPD") y aplica el color correspondiente automáticamente.
2.  **Auto-Ajuste de Ancho**: Calcula el largo del texto más largo de la columna y ajusta el ancho del Excel.
3.  **Hojas Múltiples**: Genera una hoja por Misión ("Mision 1", "Mision 2") y una hoja "Carga Masiva" (si aplica).

## ⚠️ Puntos de Falla
*   **Dependencia de `openpyxl`**: Si la librería falla o falta, el script puede degradarse a guardar un CSV plano o fallar silenciosamente (dependiendo del try/catch).
*   **Excel Abierto**: Si el usuario tiene el archivo `Rev_Mision...xlsx` abierto, el script fallará al intentar sobrescribirlo ("PermissionError"). Es el error #1 de soporte.
