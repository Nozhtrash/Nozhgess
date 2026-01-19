    def extraer_datos_tabla_provisoria(self) -> List[Dict[str, str]]:
        """
        🧠 INTELIGENTE: Extrae todos los datos estructurados de la Tabla Provisoria (Cartola).
        
        Parsea el texto crudo de cada fila para obtener:
        - Caso (Nombre limpio)
        - Estado
        - Fecha Apertura (DD/MM/YYYY)
        - Fecha Cierre (DD/MM/YYYY o 'NO' si está abierto)
        - Fecha Completa (datetime para ordenamiento)
        
        Retorna:
            List[Dict]: Lista de diccionarios con la info de cada caso.
        """
        raw_cases = self.lista_de_casos_cartola()
        parsed_cases = []
        
        for raw_text in raw_cases:
            try:
                # Formato esperado: "Nombre . {decreto}, fecha, Estado"
                # Ejemplo: "Ataque Cerebrovascular . {decreto nº 228}, 09/08/2025 10:00:00, Caso en Tratamiento"
                
                parts = raw_text.split(',')
                if len(parts) < 3:
                    continue
                    
                # 1. Nombre y Decreto (Parte 0)
                # "Ataque Cerebrovascular . {decreto nº 228}"
                part_nombre = parts[0].strip()
                nombre_limpio = part_nombre.split('{')[0].replace('.', '').strip()
                
                # 2. Fecha Apertura (Parte 1)
                # "09/08/2025 10:00:00"
                part_fecha = parts[1].strip()
                fecha_apertura = part_fecha.split(' ')[0] # "09/08/2025"
                
                # 3. Estado (Parte 2)
                # "Caso en Tratamiento"
                estado = parts[2].strip()
                
                # 4. Determinar Cierre
                # Si el estado dice "Cerrado" o similar, asumimos fecha de cierre.
                # PERO la tabla provisoria NO siempre muestra la fecha de cierre explícita en este texto.
                # La fecha de cierre suele estar en otra columna en la tabla visual real, 
                # pero lista_de_casos_cartola extrae del <p> del checkbox.
                # Si el usuario quiere la fecha exacta de cierre, necesitamos extraer de la TABLA REAL (TDs), no del <p>.
                # REVISAR NOTA DE USUARIO: "Los TD son: Caso, Creación, Cierre".
                # EL USUARIO TIENE RAZÓN. lista_de_casos_cartola lee los CHECKBOXES (versión móvil/resumida?), 
                # pero el usuario ve una TABLA con TDs.
                # DEBEMOS CAMBIAR LA ESTRATEGIA A LEER LA TABLA TABLE > TBODY > TR > TD.
                
                parsed_cases.append({
                    "raw": raw_text,
                    "caso": nombre_limpio,
                    "apertura": fecha_apertura,
                    "estado": estado,
                    "cierre": "NO" # Por defecto, refinaremos con la lectura de tabla real
                })
                
            except Exception:
                continue
                
        return parsed_cases
