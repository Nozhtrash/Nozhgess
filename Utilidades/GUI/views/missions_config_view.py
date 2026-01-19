# E_GUI/views/missions_config_view.py
# -*- coding: utf-8 -*-
"""
Vista de Editor de Configuración de Misión (Formulario Visual).
Reemplaza la edición de código crudo.
"""
import customtkinter as ctk
import os
import sys
from tkinter import messagebox, filedialog

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(ruta_proyecto)

from Utilidades.Principales.MissionConfigParser import MissionConfigHandler

class MissionsConfigView(ctk.CTkFrame):
    def __init__(self, master, colors: dict, **kwargs):
        super().__init__(master, fg_color=colors["bg_primary"], corner_radius=0, **kwargs)
        self.colors = colors
        self.config_path = os.path.join(ruta_proyecto, "Mision_Actual", "Mision_Actual.py")
        self.handler = None
        self.data_cache = {}

        # --- Header ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(
            header,
            text="🛠️ Editor de Misión",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=colors["text_primary"]
        ).pack(side="left")
        
        self.save_btn = ctk.CTkButton(
            header,
            text="💾 Guardar Cambios",
            font=ctk.CTkFont(weight="bold"),
            fg_color=colors["success"],
            hover_color="#2ecc71",
            width=140,
            command=self._save_changes
        )
        self.save_btn.pack(side="right")

        # --- Scrollable Form ---
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        self._load_data()

    def _load_data(self):
        try:
            self.handler = MissionConfigHandler(self.config_path)
            self.data_cache = self.handler.get_config()
            self._build_form()
        except Exception as e:
            ctk.CTkLabel(
                self.scroll,
                text=f"Error cargando configuración:\n{e}",
                text_color=self.colors["error"]
            ).pack(pady=20)

    def _build_form(self):
        # Limpiar view
        for w in self.scroll.winfo_children(): w.destroy()
        
        d = self.data_cache
        m = d.get("mission_data", {})
        
        # 1. Configuración General (Rutas y Nombre)
        self._section("🏠 Configuración General")
        
        self.entry_name = self._field("Nombre de la Misión", d.get("NOMBRE_DE_LA_MISION", ""))
        self.entry_path_in = self._file_field("Ruta Archivo Entrada (Excel)", d.get("RUTA_ARCHIVO_ENTRADA", ""))
        self.entry_path_out = self._folder_field("Carpeta Salida", d.get("RUTA_CARPETA_SALIDA", ""))
        
        # 2. Configuración de Misión (Lógica)
        self._section("🎯 Lógica de Búsqueda")
        
        self.entry_fam = self._field("Familia (SIGGES)", m.get("familia", ""))
        self.entry_esp = self._field("Especialidad (SIGGES)", m.get("especialidad", ""))
        
        # Keywords (List to String)
        kws = ", ".join(m.get("keywords", []))
        self.entry_kws = self._field("Palabras Clave (separar por coma)", kws)
        
        # 3. Toggles de Motor
        self._section("⚙️ Motor de Revisión")
        
        self.var_ipd = self._switch("Revisar IPD", d.get("REVISAR_IPD", True))
        self.var_oa = self._switch("Revisar OA", d.get("REVISAR_OA", True))
        self.entry_reintentos = self._field("Max Reintentos", str(d.get("MAX_REINTENTOS_POR_PACIENTE", 5)))

    # --- Helpers de UI ---
    def _section(self, title):
        ctk.CTkLabel(
            self.scroll, text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["accent"]
        ).pack(anchor="w", pady=(20, 10))
        ctk.CTkFrame(self.scroll, height=2, fg_color=self.colors["bg_card"]).pack(fill="x", pady=(0, 10))

    def _field(self, label, value):
        f = ctk.CTkFrame(self.scroll, fg_color="transparent")
        f.pack(fill="x", pady=5)
        ctk.CTkLabel(f, text=label, width=200, anchor="w", text_color=self.colors["text_secondary"]).pack(side="left")
        e = ctk.CTkEntry(f, fg_color=self.colors["bg_secondary"])
        e.pack(side="left", fill="x", expand=True)
        e.insert(0, str(value))
        return e

    def _file_field(self, label, value):
        f = ctk.CTkFrame(self.scroll, fg_color="transparent")
        f.pack(fill="x", pady=5)
        ctk.CTkLabel(f, text=label, width=200, anchor="w", text_color=self.colors["text_secondary"]).pack(side="left")
        e = ctk.CTkEntry(f, fg_color=self.colors["bg_secondary"])
        e.pack(side="left", fill="x", expand=True)
        e.insert(0, str(value))
        
        btn = ctk.CTkButton(f, text="📂", width=40, command=lambda: self._browse_file(e))
        btn.pack(side="right", padx=(5,0))
        return e

    def _folder_field(self, label, value):
        f = ctk.CTkFrame(self.scroll, fg_color="transparent")
        f.pack(fill="x", pady=5)
        ctk.CTkLabel(f, text=label, width=200, anchor="w", text_color=self.colors["text_secondary"]).pack(side="left")
        e = ctk.CTkEntry(f, fg_color=self.colors["bg_secondary"])
        e.pack(side="left", fill="x", expand=True)
        e.insert(0, str(value))
        
        btn = ctk.CTkButton(f, text="📂", width=40, command=lambda: self._browse_folder(e))
        btn.pack(side="right", padx=(5,0))
        return e

    def _switch(self, label, value):
        f = ctk.CTkFrame(self.scroll, fg_color="transparent")
        f.pack(fill="x", pady=5)
        ctk.CTkLabel(f, text=label, width=200, anchor="w", text_color=self.colors["text_secondary"]).pack(side="left")
        var = ctk.BooleanVar(value=value)
        s = ctk.CTkSwitch(f, text="", variable=var, progress_color=self.colors["accent"])
        s.pack(side="left")
        return var

    def _browse_file(self, entry):
        p = filedialog.askopenfilename()
        if p:
            entry.delete(0, "end")
            entry.insert(0, p)

    def _browse_folder(self, entry):
        p = filedialog.askdirectory()
        if p:
            entry.delete(0, "end")
            entry.insert(0, p)

    def _save_changes(self):
        # Recolectar datos
        new_data = {
            "NOMBRE_DE_LA_MISION": self.entry_name.get(),
            "RUTA_ARCHIVO_ENTRADA": self.entry_path_in.get(),
            "RUTA_CARPETA_SALIDA": self.entry_path_out.get(),
            "MAX_REINTENTOS_POR_PACIENTE": int(self.entry_reintentos.get()),
            "REVISAR_IPD": self.var_ipd.get(),
            "REVISAR_OA": self.var_oa.get(),
            # Mission Data struct
            "mission_data": {
                "nombre": self.entry_name.get(), # Sync with global
                "familia": self.entry_fam.get(),
                "especialidad": self.entry_esp.get(),
                "keywords": [k.strip() for k in self.entry_kws.get().split(",") if k.strip()]
            }
        }
        
        try:
            self.handler.update_config(new_data)
            messagebox.showinfo("Éxito", "Misión actualizada correctamente.\nListo para ejecutar.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")
