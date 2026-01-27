# Configuración Segura (`App/src/config/secure_config.py`)

## 📌 Propósito
Módulo "Blindado" para gestionar la configuración sensible de la misión.
Permite sobreescribir cualquier variable de `mission_config.json` usando Variables de Entorno, ideal para despliegues CI/CD o entornos seguros donde no se quiere tocar el archivo JSON.

## 🛡️ Mecanismo de Carga Híbrida (`_load_hybrid_config`)
1.  **Carga Base**: Lee `mission_config.json` (UTF-8).
2.  **Sobreescritura por ENV**: Itera sobre un diccionario de mapeo.
    *   Ej: Si existe `os.environ["NOZHGESS_INPUT_PATH"]`, reemplaza el valor de `RUTA_ARCHIVO_ENTRADA`.
    *   **Type Casting Seguro**: Convierte automáticamente strings de ENV a `int` o `bool` según la clave (ej: `"true"` -> `True`).

## 🔍 Validation (`validate_critical_config`)
Antes de iniciar, el sistema lanza esta función que verifica:
*   Existencia física de `RUTA_ARCHIVO_ENTRADA` y `EDGE_DRIVER_PATH`.
*   Integridad de tipos (que los índices de columnas sean enteros positivos).

## ♻️ Restore from Backup
Incluye un mecanismo de "Undo" (`restore_from_backup`).
Si la configuración se corrompe, el sistema puede revertir automáticamente a `mission_config_backup.json` y recargar en caliente sin reiniciar la App.
