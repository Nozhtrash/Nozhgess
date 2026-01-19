    def extraer_tabla_provisoria_completa(self) -> List[Dict[str, str]]:
        """
        🧠 INTELIGENTE: Lee la TABLA HTML real de la cartola (no los checkboxes).
        
        Extrae información detallada:
        - Columna 1: Caso (Nombre)
        - Columna 3: Fecha Creación
        - Columna 6: Fecha Cierre
        
        Retorna:
            List[Dict]: {
                "caso": "Ataque Cerebrovascular",
                "estado": "Caso en Tratamiento", # Se infiere o lee de otra col si existe
                "apertura": "dd/mm/yyyy",
                "cierre": "dd/mm/yyyy" o "NO",
                "raw_fecha_creacion": datetime obj
            }
        """
        # XPath proporcionado por usuario para el tbody
        # //*[@id="root"]/main/div[3]/div[2]/div[1]/div[3]/div/table/tbody
        # Usaremos uno relativo más robusto por si cambia el ID root
        xpath_tbody = "//div[contains(@class,'contBox')]/div/div/table/tbody"
        
        tbody = self._find(xpath_tbody, "presence", "tabla_provisoria")
        if not tbody:
            # Fallback a los selectores exactos del usuario si el genérico falla
            xpath_exacto = "/html/body/div/main/div[3]/div[2]/div[1]/div[3]/div/table/tbody"
            tbody = self._find(xpath_exacto, "presence", "tabla_provisoria_exacto")
            
        if not tbody:
            return []

        filas = tbody.find_elements(By.TAG_NAME, "tr")
        datos_casos = []
        
        for tr in filas:
            try:
                tds = tr.find_elements(By.TAG_NAME, "td")
                if len(tds) < 6:
                    continue
                    
                # 1. Caso (Nombre) - TD 1
                raw_nombre = tds[0].text.strip()
                # Limpiar: "Ataque Cerebrovascular . {decreto...}" -> "Ataque Cerebrovascular"
                nombre_limpio = raw_nombre.split('{')[0].replace('.', '').strip()
                
                # 2. Estado - TD 4 (Inferido del ejemplo del usuario: "Caso en Tratamiento")
                # El usuario dijo: "Tabla Provisoria... TD Caso... TD Creación... TD Cierre"
                # Pero en su ejemplo de texto pegado se ve: "Caso... Fecha... Estado... Hospital... Cierre"
                # Las columnas parecen ser:
                # 1: Caso
                # 2: Decreto? (o parte del 1)
                # 3: Fecha Creacion
                # 4: Estado (ej: Caso en Tratamiento)
                # 5: Hospital
                # 6: Cierre
                
                estado = tds[3].text.strip() # Asumimos col 4 (índice 3)
                
                # 3. Apertura - TD 3
                raw_apertura = tds[2].text.strip() # "09/08/2025 10:00:00"
                apertura = raw_apertura.split(' ')[0] # "09/08/2025"
                
                # 4. Cierre - TD 6
                raw_cierre = tds[5].text.strip() # "30/10/2023" o "Sin Informacion"
                # Formatear cierre
                if not raw_cierre or raw_cierre.lower() in ["sin informacion", "sin información", "-"]:
                    cierre = "NO"
                else:
                    cierre = raw_cierre.split(' ')[0]
                    
                # Guardamos para análisis inteligente
                datos_casos.append({
                    "caso": nombre_limpio,
                    "estado": estado,
                    "apertura": apertura,
                    "cierre": cierre,
                    "fecha_obj": dparse(apertura), # Para ordenar por reciente
                    "indice_tabla": filas.index(tr) # Para clickear si fuese necesario (aunque clickeamos checkboxes)
                })
                
            except Exception:
                continue
                
        return datos_casos
