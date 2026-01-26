# Optimización Conservadora de Spinner Wait

## Cambio Aplicado

```python
# ANTES
appear_timeout=1

# DESPUÉS  
appear_timeout=0.5
```

## Razón Técnica

- Spinner típicamente aparece en <300ms
- 0.5s da margen de seguridad de 200ms extra
- WebDriverWait detecta el spinner aunque aparezca después

## Seguridad

✅ CONSERVADOR: No es agresivo (0.5s no 0.2s)
✅ SEGURO: WebDriverWait sigue funcionando correctamente
✅ REVERSIBLE: Backup creado

## Impacto Esperado

- Ahorro: ~0.5s por paciente
- De 12s → 11.5s por paciente
- Total: ~43 segundos en 87 pacientes

## Rollback

```powershell
Copy-Item "Conexiones.py.pre_optimization_*" "Conexiones.py"
```

## Monitoreo

Observar primeros 5 pacientes:

- ¿Errores de timeout?
- ¿Funciona igual?
- Si falla → revertir inmediatamente
