# Changelog - NOZHGESS

## 📦 [v2.2-CLEAN-UI] - 2026-01-08
**Status:** ✅ RELEASED
**Focus:** Clean UX, Production Silence & Debug Mode.

### ✨ UI & Experiencia
- **Interfaz Limpia:** Implementado sistema silencioso. La terminal muestra SOLO el resumen del paciente en 4 líneas.
- **Formato Visual:** Resumen optimizado con emojis dobles ⚠️ y separadores largos.
- **Debug Mode:** Nuevo archivo `D_Principales/DEBUG.py` para activar logs detallados.

### 🚀 Mejoras
- **Cero Ruido:** Eliminados logs ("Expandir caso", "Leer IPD") en modo producción.
- **Conexiones.py:** Refactorizado con `should_show_timing()` en todos los puntos.

## 📦 [v2.1-TIER-SSS] - 2026-01-08
**Status:** ✅ RELEASED / STABLE
**Focus:** Extreme Performance, Intelligent Timing, & Bug Fixes.

### 🚀 Optimizations
- **JavaScript Mini-Tabla:** Implemented direct DOM reading via JS.
  - Performance: **13ms** average (down from 650ms).
  - Robustness: Added fallback to Python parsing if JS fails.
- **Global Cumulative Timing:**
  - Switched from per-patient timer reset to a single script-level timer.
  - Exposed hidden gaps (e.g., 2.7s transition delay) that were previously masked.
- **Smart Navigation:**
  - Implemented `instant_check` in `asegurar_en_busqueda` to skip navigation if already on the correct page.
  - Removed redundant `asegurar_menu_desplegado()` calls (saved ~1.5s per retry/navigation).
- **Timeout Reduction:**
  - `cartola_click_ir`: 0.5s → 0.2s.
  - `search_wait_results`: Reduced safe buffer.

### 🐛 Bug Fixes
- **Critical Crash:** Fixed missing `import time` and `from colorama ...` in `Conexiones.py`.
- **JS Scope Error:** Fixed `NameError: name '_extraer_fecha' is not defined` by moving date parsing to Python side and renaming to `_parse_fecha`.
- **Fake 0ms Timing:** Removed incorrect "Transición: 0ms" log that was misinforming debugging attempts.

---

## [v2.0] - 2026-01-07
**Status:** Released
- Initial "Tier S" structure.
- Implementation of `Mini_Tabla` module.
- Excel reporting features.

## [v1.0 - v1.5]
- Legacy versions. High delay (20s+ per patient).
