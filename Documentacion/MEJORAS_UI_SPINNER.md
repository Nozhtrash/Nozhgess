# Mejoras UI Spinner y Loading Dialog

## Contexto
El "Spinner" o indicador de carga es un punto crítico de la aplicación. Su detección es variable (0.5s a 1m+), lo que causa fallos en el script de automatización si no se maneja "inteligentemente".

## Análisis DOM (Fuente: DevTools 2026-02-11)

La estructura real del spinner en el DOM es:
```html
<body>
  <div id="root">
    <dialog class="loading" open="">
      <div class="circulo"></div>
    </dialog>
  </div>
</body>
```

### Problemas Detectados
1. **Centrado Redundante**: Se usa `position: fixed` y `transform: translate` tanto en `dialog` como en `.loading`.
2. **Pseudo-clase `:modal`**: Se está estilizando `.loading:modal`, pero el diálogo se abre con el atributo `open` (no `showModal()`), por lo que estos estilos **no se aplican**.
3. **Renderizado de Texto**: El selector global `* { image-rendering: pixelated; }` afecta a toda la app, degradando la calidad del texto.

## Solución CSS Propuesta

### 1. CSS Optimizado para `.loading`
Centralizar el estilo en la clase `.loading` y eliminar redundancias.

```css
.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 120px;
  height: 120px;
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%); /* Centrado absoluto */
  background: transparent;
  border: none;
  box-shadow: none;
  z-index: 9999; /* Asegurar visibilidad */
}
```

### 2. Uso correcto de Dialog
Si se desea usar la API nativa de modal:
- Usar JS: `dialog.showModal()`
- CSS: `dialog::backdrop` para el fondo oscuro.

Si se mantiene el uso actual (`open=""`):
- Los estilos deben apuntar directamente a `dialog[open]` o `.loading`.

### 3. Corrección Global
Restringir `image-rendering: pixelated` solo a imágenes o canvas:
```css
img, canvas {
  image-rendering: pixelated;
}
```

## Estrategia de Detección (Automation Script)

Para resolver la inestabilidad en la detección del spinner, se implementará un **Detector Inteligente (Smart Detector)** en Python/Selenium:

### Lógica Propuesta
1. **Inyección JS Directa**: No usar `find_element` de Selenium (lento). Usar `driver.execute_script("return document.querySelector('dialog.loading[open]') != null")`.
2. **Fase de Detección Rápida (0-500ms)**:
    - Sondear cada 50ms.
    - Si aparece -> Ir a Fase de Espera.
    - Si NO aparece tras 500ms -> Asumir que no hubo carga y continuar inmediatamente.
3. **Fase de Espera Activa**:
    - Si se detectó, esperar hasta que desaparezca.
    - Sondear cada 100ms.
    - **Timeout Dinámico**: Si dura más de X tiempo (ej. 60s), registrar "Spinner Stuck" pero intentar continuar o refrescar según severidad.

Esto elimina las "esperas ciegas" y hace que el script sea tan rápido como la UI lo permita.
