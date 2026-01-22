import customtkinter as ctk
from typing import Dict, Type, Any

class ViewManager:
    """
    Gestor de Vistas Modular.
    - Lazy Loading: Solo instancia vistas al necesitarlas.
    - Caching: Mantiene vistas vivas (opcional).
    - Navegación: show("view_name").
    """
    
    def __init__(self, container: ctk.CTkFrame, context: dict = None):
        self.container = container
        self.context = context or {}
        
        # Registro de Clases de Vista: {name: ViewClass}
        self._registry: Dict[str, Type] = {}
        
        # Instancias activas: {name: instance}
        self._instances: Dict[str, Any] = {}
        
        self.current_view_name = None

    def register(self, name: str, view_cls: Type, **kwargs):
        """Registra una clase de vista con argumentos opcionales para __init__."""
        self._registry[name] = (view_cls, kwargs)

    def show(self, name: str):
        """Muestra la vista indicada, instanciándola si es necesario."""
        if name not in self._registry and name not in self._instances:
            print(f"Error: Vista '{name}' no registrada.")
            return

        # 1. Ocultar actual
        if self.current_view_name:
            curr = self._instances.get(self.current_view_name)
            if curr:
                curr.grid_forget()
                if hasattr(curr, "on_hide"): curr.on_hide()
        
        # 2. Get/Create instancia
        try:
            if name not in self._instances:
                # Lazy Instantiation
                if name not in self._registry:
                     return # Should not happen check above
                     
                view_cls, view_kwargs = self._registry[name]
                
                # Merge context colors with view specific kwargs
                init_kwargs = view_kwargs.copy()
                init_kwargs["colors"] = self.context.get("colors", {})
                
                # Instanciar
                instance = view_cls(self.container, **init_kwargs)
                self._instances[name] = instance
        except Exception as e:
            print(f"❌ Error instanciando vista '{name}': {e}")
            import traceback
            traceback.print_exc()
            # Placeholder de error para que no quede vacía la pantalla
            error_view = ctk.CTkFrame(self.container, fg_color="#442222")
            ctk.CTkLabel(
                error_view, 
                text=f"⚠️ Error al cargar '{name}'\n\n{str(e)}",
                font=("Segoe UI", 14),
                text_color="white"
            ).pack(expand=True, padx=20, pady=20)
            self._instances[name] = error_view

        view = self._instances[name]
        
        # 3. Mostrar nueva
        view.grid(row=0, column=0, sticky="nsew")
        self.current_view_name = name
        
        # Lifecycle hook
        if hasattr(view, "on_show"):
            view.on_show()

    def get_view(self, name: str):
        return self._instances.get(name)

    def refresh_theme(self, new_colors: dict):
        """Propaga cambios de tema a vistas activas (o a todas)."""
        self.context["colors"] = new_colors
        # Destruir caché para forzar recreate con nuevos colores (Estrategia Brutal pero segura para legacy)
        # O llamar a update_colors() si implementan la interfaz.
        
        # Estrategia Híbrida:
        # 1. Si tienen update_colors, usarlo.
        # 2. Si no, destruir y el próximo show() las recreará.
        
        for name, view in list(self._instances.items()):
            if hasattr(view, "update_colors"):
                view.update_colors(new_colors)
            else:
                # Legacy view sin soporte de tema dinámico -> Destroy
                view.destroy()
                del self._instances[name]
        
        # Restaurar vista actual si murió
        if self.current_view_name and self.current_view_name not in self._instances:
            self.show(self.current_view_name)
