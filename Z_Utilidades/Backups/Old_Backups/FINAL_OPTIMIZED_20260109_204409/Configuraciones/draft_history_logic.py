def buscar_inteligencia_historia(sigges, root, estado_caso: str) -> Dict[str, str]:
    """
    🧠 Analiza TODA la historia clínica (OAs) para determinar aptitud y buscar folios.
    
    Reglas:
    1. ¿Apto? = "SI" si el estado es seguimiento O si existe "Seguimiento" en OAs/SICs antiguas.
    2. Folios Globales: Busca CODIGOS_FOLIO_BUSCAR en TODAS las OAs (sin límite).
    
    Args:
        sigges: Objeto driver
        root: Elemento raíz del caso expandido
        estado_caso: Estado actual del caso (para chequeo rápido)
        
    Returns:
        Dict con {"apto": "SI"/"NO", "obs_folio": "..."}
    """
    es_apto = False
    
    # 1. Chequeo rápido por estado actual
    if "seguimiento" in (estado_caso or "").lower():
        es_apto = True
        
    # Extraer TODAS las OAs (n=0) para análisis profundo
    # fechas, derivados, diagnósticos, códigos, folios
    f, d, diag, c, folios = sigges.leer_oa_desde_caso(root, 0)
    
    # 2. Búsqueda de "Seguimiento" en historia
    if not es_apto: # Si ya es apto por estado, no necesitamos buscar exhaustivamente esto
        kw = "seguimiento"
        for txt in (d + diag): # Buscar en Derivados y Diagnósticos
            if kw in (txt or "").lower():
                es_apto = True
                break
                
    # 3. Búsqueda Global de Folios (Feature solicitada)
    # "quiero que se revisen todas las OA existentes del caso a ver si está uno de los códigos que puse"
    obs_folio_parts = []
    
    # Lista de códigos a buscar (definida en Mision_Actual, importada aquí via GLOBAL o param)
    # Asumimos que CODIGOS_FOLIO_BUSCAR está importado de Mision_Actual
    targets = CODIGOS_FOLIO_BUSCAR if OBSERVACION_FOLIO_FILTRADA else []
    
    if targets and folios:
        for i, folio_num in enumerate(folios):
            # Limpieza básica
            f_clean = str(folio_num).strip()
            
            # Chequear si este folio es uno de los buscados (si hay targets)
            # O si no hay targets, quizás no debemos reportar nada acá para no spamear?
            # El usuario dijo: "si la encuentra, pone en columna observacion folio..."
            
            # El requerimiento es confuso sobre "código" vs "folio". 
            # Dijo: "si en prestaciones... un código x uso el folio del código y...".
            # Pero en la sección de OA dijo: "Codigos OA a buscar... CODIGOS_FOLIO_BUSCAR".
            # Asumiremos que busca si el CÓDIGO DE LA PRESTACION/OA coincide con la lista.
            # En leer_oa, la variable 'c' es la lista de Códigos (ej: 0305015) y 'folios' son los números de folio.
            # LA LISTA SE LLAMA CODIGOS_FOLIO_BUSCAR. Y contiene códigos tipo 1902003 (Códigos de prestación).
            
            codigo_oa = c[i] if i < len(c) else ""
            
            if codigo_oa in targets:
                # Encontrado!
                fecha_oa = f[i] if i < len(f) else ""
                obs_folio_parts.append(f"{codigo_oa} / {fecha_oa} / {f_clean} / SI")
                
    obs_folio_final = " | ".join(obs_folio_parts)
    
    return {
        "apto": "SI" if es_apto else "NO",
        "obs_folio": obs_folio_final
    }
