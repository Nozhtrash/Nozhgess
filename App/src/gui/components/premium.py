# Utilidades/GUI/components/premium.py
# -*- coding: utf-8 -*-
"""
==============================================================================
                    COMPONENTES PREMIUM - NOZHGESS v2.0
==============================================================================
Componentes de UI reutilizables con diseño premium:
- PremiumCard: Card con sombra y hover
- PremiumButton: Botón con efectos
- GradientButton: Botón con gradiente
- StatCard: Card para estadísticas
- SectionHeader: Encabezado de sección
- LoadingSpinner: Indicador de carga
"""
import customtkinter as ctk
from typing import Optional, Callable


class PremiumCard(ctk.CTkFrame):
    """
    Card premium con sombra sutil, borde y efectos hover.
    
    Args:
        parent: Widget padre
        colors: Diccionario de colores del tema
        hover: Si activar efecto hover (default: True)
        padding: Padding interno (default: 16)
    """
    
    def __init__(self, parent, colors: dict, hover: bool = True, 
                 padding: int = 16, **kwargs):
        super().__init__(
            parent,
            fg_color=colors.get("bg_card", "#21262d"),
            corner_radius=16,
            border_width=1,
            border_color=colors.get("border", "#30363d"),
            **kwargs
        )
        
        self.colors = colors
        self.padding = padding
        self.hover_enabled = hover
        
        # Contenedor interno con padding
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=padding, pady=padding)
        
        # Efectos hover
        if hover:
            self.bind("<Enter>", self._on_enter)
            self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Efecto al entrar hover."""
        self.configure(border_color=self.colors.get("accent", "#00f2c3"))
    
    def _on_leave(self, event):
        """Efecto al salir hover."""
        self.configure(border_color=self.colors.get("border", "#30363d"))
    
    def get_content_frame(self) -> ctk.CTkFrame:
        """Retorna el frame de contenido para agregar widgets."""
        return self.content


class PremiumButton(ctk.CTkButton):
    """
    Botón premium con efectos de hover avanzados.
    
    Args:
        parent: Widget padre
        colors: Diccionario de colores
        variant: "primary", "secondary", "ghost", "danger"
    """
    
    def __init__(self, parent, colors: dict, variant: str = "primary",
                 text: str = "", icon: str = "", **kwargs):
        
        # Configurar colores según variante
        if variant == "primary":
            fg = colors.get("accent", "#00f2c3")
            hover = colors.get("success", "#3fb950")
            text_color = colors.get("bg_primary", "#0d1117")
        elif variant == "secondary":
            fg = colors.get("bg_card", "#21262d")
            hover = colors.get("bg_elevated", "#30363d")
            text_color = colors.get("text_primary", "#f0f6fc")
        elif variant == "ghost":
            fg = "transparent"
            hover = colors.get("bg_hover", "#484f58")
            text_color = colors.get("text_primary", "#f0f6fc")
        elif variant == "danger":
            fg = colors.get("error", "#f85149")
            hover = "#d73a49"
            text_color = "#ffffff"
        else:
            fg = colors.get("accent", "#00f2c3")
            hover = colors.get("success", "#3fb950")
            text_color = colors.get("bg_primary", "#0d1117")
        
        # Texto con icono
        display_text = f"{icon}  {text}" if icon else text
        
        super().__init__(
            parent,
            text=display_text,
            fg_color=fg,
            hover_color=hover,
            text_color=text_color,
            corner_radius=12,
            height=44,
            font=ctk.CTkFont(size=13, weight="bold"),
            **kwargs
        )
        
        self.colors = colors
        self.variant = variant


class GradientButton(ctk.CTkButton):
    """
    Botón con efecto de gradiente simulado.
    Nota: CustomTkinter no soporta gradientes nativos,
    usamos un color sólido con hover que simula el efecto.
    """
    
    def __init__(self, parent, colors: dict, gradient: str = "primary",
                 text: str = "", **kwargs):
        
        from src.gui.theme import get_gradient_colors
        
        gradient_colors = get_gradient_colors(gradient)
        
        super().__init__(
            parent,
            text=text,
            fg_color=gradient_colors[0],
            hover_color=gradient_colors[1],
            text_color="#ffffff",
            corner_radius=12,
            height=52,
            font=ctk.CTkFont(size=15, weight="bold"),
            **kwargs
        )
        
        self.gradient_colors = gradient_colors


class StatCard(ctk.CTkFrame):
    """
    Card para mostrar una estadística con icono, título y valor.
    
    Args:
        parent: Widget padre
        colors: Diccionario de colores
        icon: Emoji o icono
        title: Título de la estadística
        value: Valor a mostrar
        trend: Opcional - "up", "down", "neutral"
    """
    
    def __init__(self, parent, colors: dict, icon: str = "📊",
                 title: str = "Título", value: str = "0",
                 trend: Optional[str] = None, **kwargs):
        super().__init__(
            parent,
            fg_color=colors.get("bg_card", "#21262d"),
            corner_radius=16,
            border_width=1,
            border_color=colors.get("border", "#30363d"),
            **kwargs
        )
        
        self.colors = colors
        
        # Layout interno
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=16, pady=16)
        
        # Header con icono y título
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", anchor="w")
        
        ctk.CTkLabel(
            header,
            text=icon,
            font=ctk.CTkFont(size=18)
        ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text=title.upper(),
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=colors.get("text_muted", "#6e7681")
        ).pack(side="left", padx=(8, 0))
        
        # Valor grande
        value_frame = ctk.CTkFrame(content, fg_color="transparent")
        value_frame.pack(fill="x", pady=(8, 0))
        
        self.value_label = ctk.CTkLabel(
            value_frame,
            text=value,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=colors.get("text_primary", "#f0f6fc"),
            wraplength=180,
            justify="left"
        )
        self.value_label.pack(side="left", anchor="w")
        
        # Indicador de tendencia
        if trend:
            trend_icon = "↑" if trend == "up" else "↓" if trend == "down" else "→"
            trend_color = (colors.get("success", "#3fb950") if trend == "up" 
                          else colors.get("error", "#f85149") if trend == "down"
                          else colors.get("text_muted", "#6e7681"))
            
            ctk.CTkLabel(
                value_frame,
                text=trend_icon,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=trend_color
            ).pack(side="right")
        
        # Efecto hover
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        self.configure(border_color=self.colors.get("accent", "#00f2c3"))
    
    def _on_leave(self, event):
        self.configure(border_color=self.colors.get("border", "#30363d"))
    
    def update_value(self, new_value: str):
        """Actualiza el valor mostrado."""
        self.value_label.configure(text=new_value)


class SectionHeader(ctk.CTkFrame):
    """
    Encabezado de sección con icono y título.
    
    Args:
        parent: Widget padre
        colors: Diccionario de colores
        icon: Emoji o icono
        title: Título de la sección
        action_text: Texto de botón de acción (opcional)
        action_command: Comando del botón (opcional)
    """
    
    def __init__(self, parent, colors: dict, icon: str = "📋",
                 title: str = "Sección", action_text: Optional[str] = None,
                 action_command: Optional[Callable] = None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.colors = colors
        
        # Label con icono y título
        label = ctk.CTkLabel(
            self,
            text=f"{icon}  {title.upper()}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=colors.get("text_secondary", "#8b949e")
        )
        label.pack(side="left")
        
        # Botón de acción opcional
        if action_text and action_command:
            action_btn = ctk.CTkButton(
                self,
                text=action_text,
                font=ctk.CTkFont(size=11),
                fg_color="transparent",
                hover_color=colors.get("bg_hover", "#484f58"),
                text_color=colors.get("accent", "#00f2c3"),
                width=80,
                height=28,
                corner_radius=6,
                command=action_command
            )
            action_btn.pack(side="right")


class LoadingSpinner(ctk.CTkFrame):
    """
    Indicador de carga animado.
    Nota: CustomTkinter no tiene spinner nativo, 
    usamos texto animado.
    """
    
    def __init__(self, parent, colors: dict, size: int = 32, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.colors = colors
        self.size = size
        self.frames = ["◐", "◓", "◑", "◒"]
        self.current_frame = 0
        self.is_spinning = False
        
        self.spinner_label = ctk.CTkLabel(
            self,
            text=self.frames[0],
            font=ctk.CTkFont(size=size),
            text_color=colors.get("accent", "#00f2c3")
        )
        self.spinner_label.pack()
    
    def start(self):
        """Inicia la animación."""
        self.is_spinning = True
        self._animate()
    
    def stop(self):
        """Detiene la animación."""
        self.is_spinning = False
    
    def _animate(self):
        """Anima el spinner."""
        if not self.is_spinning:
            return
        
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.spinner_label.configure(text=self.frames[self.current_frame])
        self.after(100, self._animate)


class InfoBadge(ctk.CTkFrame):
    """
    Badge para mostrar información de estado.
    
    Args:
        parent: Widget padre
        colors: Diccionario de colores
        text: Texto del badge
        variant: "success", "warning", "error", "info", "neutral"
    """
    
    def __init__(self, parent, colors: dict, text: str = "",
                 variant: str = "neutral", **kwargs):
        
        # Determinar color según variante
        if variant == "success":
            bg = colors.get("success", "#3fb950")
        elif variant == "warning":
            bg = colors.get("warning", "#d29922")
        elif variant == "error":
            bg = colors.get("error", "#f85149")
        elif variant == "info":
            bg = colors.get("info", "#58a6ff")
        else:
            bg = colors.get("bg_elevated", "#30363d")
        
        super().__init__(
            parent,
            fg_color=bg,
            corner_radius=12,
            **kwargs
        )
        
        label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#ffffff" if variant != "neutral" else colors.get("text_primary", "#f0f6fc")
        )
        label.pack(padx=10, pady=4)
