
import customtkinter as ctk
from typing import List, Dict, Any, Callable

class FrequencyListEditor(ctk.CTkFrame):
    """
    Editor para lista de reglas de frecuencia.
    Estilo profesional, input validado.
    """
    def __init__(self, master, data_list: List[Dict], onChange: Callable = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.data_list = data_list
        self.onChange = onChange
        
        # --- INPUT HEADER SECTION ---
        self.add_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.add_frame.pack(fill="x", pady=(0, 5))
        
        # Code
        self.ent_code = ctk.CTkEntry(self.add_frame, placeholder_text="Código", width=90)
        self.ent_code.pack(side="left", padx=(0, 5))
        
        # Type
        self.var_type = ctk.StringVar(value="Mes")
        ctk.CTkOptionMenu(self.add_frame, values=["Mes", "Año", "Vida"], variable=self.var_type, width=80).pack(side="left", padx=5)
        
        # Qty
        self.ent_qty = ctk.CTkEntry(self.add_frame, placeholder_text="Cant.", width=50)
        self.ent_qty.pack(side="left", padx=5)
        self.ent_qty.insert(0, "1")
        
        # Label
        self.ent_lbl = ctk.CTkEntry(self.add_frame, placeholder_text="Etiqueta / Obs", width=120)
        self.ent_lbl.pack(side="left", padx=5, fill="x", expand=True)
        
        # Add Button
        ctk.CTkButton(
            self.add_frame, text="+", width=30, height=28,
            fg_color="#22c55e", hover_color="#16a34a",
            command=self._add_row
        ).pack(side="left", padx=5)
        
        # --- LIST CONTAINER ---
        self.rows_frame = ctk.CTkFrame(self, fg_color=("gray95", "gray16"), corner_radius=6)
        self.rows_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        self.refresh_rows()

    def refresh_rows(self):
        for w in self.rows_frame.winfo_children():
            w.destroy()
            
        if not self.data_list:
            ctk.CTkLabel(self.rows_frame, text="(Sin reglas de frecuencia)", text_color="gray", font=("Arial", 11)).pack(pady=10)
            return
            
        # Table Header
        h = ctk.CTkFrame(self.rows_frame, fg_color="transparent", height=24)
        h.pack(fill="x", padx=5, pady=(5,2))
        
        fonts = ("Arial", 10, "bold")
        ctk.CTkLabel(h, text="Código", width=80, anchor="w", font=fonts).pack(side="left", padx=2)
        ctk.CTkLabel(h, text="Regla", width=100, anchor="w", font=fonts).pack(side="left", padx=2)
        ctk.CTkLabel(h, text="Etiqueta", anchor="w", font=fonts).pack(side="left", padx=2, fill="x", expand=True)
        # Empty space for X button
        ctk.CTkLabel(h, text="", width=24).pack(side="right")
            
        for idx, item in enumerate(self.data_list):
            self._render_row(idx, item)

    def _render_row(self, idx, item):
        row = ctk.CTkFrame(self.rows_frame, fg_color="transparent")
        row.pack(fill="x", pady=1, padx=5)
        
        # Separator line if not first
        if idx > 0:
            ctk.CTkFrame(self.rows_frame, height=1, fg_color=("gray85", "gray25")).pack(fill="x", padx=10, before=row)
        
        # Content
        code_txt = item.get("code", "")
        rule_txt = f"{item.get('freq_qty', 1)} / {item.get('freq_type', 'Mes')}"
        lbl_txt = item.get("periodicity", "")
        
        ctk.CTkLabel(row, text=code_txt, width=80, anchor="w", font=("Arial", 12)).pack(side="left", padx=2)
        ctk.CTkLabel(row, text=rule_txt, width=100, anchor="w", text_color="#3b8ed0").pack(side="left", padx=2)
        ctk.CTkLabel(row, text=lbl_txt, anchor="w", text_color="gray70").pack(side="left", padx=2, fill="x", expand=True)
        
        # Delete
        ctk.CTkButton(
            row, text="×", width=24, height=24, 
            fg_color="transparent", text_color=("gray50", "gray70"), hover_color=("gray80", "gray25"),
            command=lambda i=idx: self.delete_row(i)
        ).pack(side="right", padx=0)

    def _add_row(self):
        code = self.ent_code.get().strip()
        if not code: return
        
        try: qty = int(self.ent_qty.get())
        except: qty = 1
        
        self.data_list.append({
            "code": code, 
            "freq_type": self.var_type.get(), 
            "freq_qty": qty, 
            "periodicity": self.ent_lbl.get().strip()
        })
        
        # Reset inputs
        self.ent_code.delete(0, "end")
        self.ent_lbl.delete(0, "end")
        self.ent_qty.delete(0, "end"); self.ent_qty.insert(0, "1")
        
        self.refresh_rows()
        if self.onChange: self.onChange()

    def delete_row(self, idx):
        if 0 <= idx < len(self.data_list):
            self.data_list.pop(idx)
            self.refresh_rows()
            if self.onChange: self.onChange()
            
    def get_data(self):
        # Return live reference (or copy if safer, but live ref standard here)
        return self.data_list
