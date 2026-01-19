def seleccionar_caso_inteligente(casos_data: List[Dict[str, Any]], kws: List[str]) -> Optional[Dict[str, Any]]:
    """
    🧠 Selecciona el MEJOR caso basándose en reglas de negocio inteligentes.
    
    Prioridad:
    1. Coincidencia de keywords (filtro inicial).
    2. Estado: Activo ("En Tratamiento", "Diagnóstico") > Cerrado.
    3. Recencia: Fecha más reciente gana dentro de su categoría de estado.
    
    Args:
        casos_data: Lista de dicts extraídos de la tabla provisoria.
        kws: Keywords para filtrar por nombre (case-insensitive).
        
    Returns:
        Dict con la info del caso seleccionado o None.
    """
    candidatos = []
    
    # 1. Filtrar por Keywords
    for c in casos_data:
        nombre = c.get("caso", "").lower()
        if not kws: # Si no hay kws, todos pasan (raro, pero posible)
            candidatos.append(c)
            continue
            
        for kw in kws:
            if kw.lower() in nombre:
                candidatos.append(c)
                break
    
    if not candidatos:
        return None
        
    # 2. Definir función de puntaje
    # Puntaje = (EsActivo * 1000000) + Timestamp
    # Así, un caso activo SIEMPRE gana a uno cerrado, y entre activos gana el más reciente.
    
    mejor_caso = None
    mejor_puntaje = -1
    
    for c in candidatos:
        estado = c.get("estado", "").lower()
        es_cerrado = "cerrado" in estado or "cierre" in estado
        es_activo = not es_cerrado
        
        # Fecha para recencia
        dt = c.get("fecha_dt", datetime.min)
        ts = dt.timestamp()
        
        # Calcular puntaje
        base_score = 10000000000 if es_activo else 0 
        score = base_score + ts
        
        if score > mejor_puntaje:
            mejor_puntaje = score
            mejor_caso = c
            
    return mejor_caso
