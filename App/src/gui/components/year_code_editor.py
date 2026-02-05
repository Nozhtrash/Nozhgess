
import customtkinter as ctk
from typing import List, Dict, Callable

class YearCodeEditor(ctk.CTkFrame):
    """
    Editor para 'Códigos por Año'. 
    Permite definir reglas específicas para antigüedad del paciente (Año 1, Año 2, etc.)
    """
    def __init__(self, master, data_list: List[Dict], colors: Dict, onChange: Callable = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.colors = colors
        
        # Normalize incoming data (handle legacy formats)
        self.items = []
        if isinstance(data_list, list):
            for item in data_list:
                norm = self._normalize_item(item)
                if norm: self.items.append(norm)
                
        self.onChange = onChange
        
        # --- ADD NEW SECTION ---
        self.add_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.add_frame.pack(fill="x", pady=5)
        
        # Input: Code
        self.ent_code = ctk.CTkEntry(self.add_frame, placeholder_text="Código (Ej: 301001)", width=120)
        self.ent_code.pack(side="left", padx=(0, 5))
        
        # Input: Freq Type
        self.var_type = ctk.StringVar(value="Mes")
        ctk.CTkOptionMenu(self.add_frame, values=["Mes", "Año", "Vida"], variable=self.var_type, width=70).pack(side="left", padx=5)
        
        # Input: Freq Qty
        self.ent_qty = ctk.CTkEntry(self.add_frame, placeholder_text="1", width=40)
        self.ent_qty.pack(side="left", padx=5)
        self.ent_qty.insert(0, "1")
        
        # Input: Label
        self.ent_lbl = ctk.CTkEntry(self.add_frame, placeholder_text="Etiqueta (Ej: Mensual)", width=120)
        self.ent_lbl.pack(side="left", padx=5, fill="x", expand=True)
        
        # Add Button
        ctk.CTkButton(
            self.add_frame, text="+ Año", width=60, 
            fg_color=self.colors.get("success", "#22c55e"),
            command=self._on_add
        ).pack(side="left", padx=5)
        
        # --- LIST SECTION ---
        self.list_cnt = ctk.CTkFrame(self, fg_color=("gray90", "gray16"), corner_radius=6)
        self.list_cnt.pack(fill="x", expand=True, pady=5)
        
        self.refresh_list()

    def _on_add(self):
        code = self.ent_code.get().strip()
        if not code: return
        
        qty = 1
        try: qty = int(self.ent_qty.get())
        except: pass
        
        new_item = {
            "code": code,
            "freq_type": self.var_type.get(),
            "freq_qty": qty,
            "periodicity": self.ent_lbl.get().strip()
        }
        
        self.items.append(new_item)
        self.refresh_list()
        
        # Clear inputs
        self.ent_code.delete(0, "end")
        self.ent_lbl.delete(0, "end")
        if self.onChange: self.onChange()

    def refresh_list(self):
        for w in self.list_cnt.winfo_children(): w.destroy()
        
        if not self.items:
            ctk.CTkLabel(self.list_cnt, text="(Sin códigos configurados para antigüedad)", text_color="gray").pack(pady=10)
            return
            
        # Header
        h = ctk.CTkFrame(self.list_cnt, fg_color="transparent", height=24)
        h.pack(fill="x", padx=5, pady=(5,2))
        ctk.CTkLabel(h, text="Antigüedad", width=80, anchor="w", font=("Arial", 11, "bold")).pack(side="left")
        ctk.CTkLabel(h, text="Regla de Código", anchor="w", font=("Arial", 11, "bold")).pack(side="left", padx=10)
            
        for i, item in enumerate(self.items):
            row = ctk.CTkFrame(self.list_cnt, fg_color="transparent")
            row.pack(fill="x", padx=5, pady=2)
            
            # Label "Año X"
            ctk.CTkLabel(row, text=f"Año {i+1}", width=80, anchor="w", font=("Arial", 12, "bold"), text_color=self.colors.get("accent", "#3b8ed0")).pack(side="left")
            
            # Summary
            desc = f"{item.get('code')} -> Freq: {item.get('freq_qty')} / {item.get('freq_type')}"
            if item.get('periodicity'): desc += f" ({item.get('periodicity')})"
            
            ctk.CTkLabel(row, text=desc, anchor="w").pack(side="left", padx=10, fill="x", expand=True)
            
            # Delete (Last Only)
            is_last = (i == len(self.items) - 1)
            if is_last:
                ctk.CTkButton(row, text="×", width=24, height=24, fg_color=self.colors.get("error", "red"),
                              command=lambda idx=i: self._remove_item(idx)).pack(side="right")
            else:
                ctk.CTkLabel(row, text="🔒", width=24).pack(side="right")

    def _remove_item(self, idx):
        if 0 <= idx < len(self.items):
            self.items.pop(idx)
            self.refresh_list()
            if self.onChange: self.onChange()

    def get_data(self):
        return self.items

    def _normalize_item(self, item):
        """Convierte datos viejos a estructura nueva dict."""
        default_struct = {"code": "", "freq_type": "Mes", "freq_qty": 1, "periodicity": "Mensual"}
        
        if isinstance(item, dict):
            # Asumimos que ya es formato nuevo
            # Ensure ints for qty
            try: item["freq_qty"] = int(item.get("freq_qty", 1))
            except: item["freq_qty"] = 1
            return {**default_struct, **item} 
        
        # Legacy: String "CODE" or List [Year, Code] -> We only care about Code now, order implies Year
        code_str = ""
        if isinstance(item, list) and len(item) >= 2:
            code_str = str(item[1]).strip()
        elif isinstance(item, str):
            # Handle "Year, Code" string if any, or just Code
            if "," in item:
                code_str = item.split(",")[1].strip() 
            else:
                code_str = item.strip()
        else:
            code_str = str(item).strip()
            
        if code_str:
            d = default_struct.copy()
            d["code"] = code_str
            d["periodicity"] = "Anual" # Default for legacy year codes
            d["freq_type"] = "Año"
            return d
        return None
