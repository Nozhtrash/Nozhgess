"""
Módulo de Logging Seguro Nozhgess
=================================
Propósito: Mejorar seguridad de logging sin cambiar estructura existente
Máscara de datos sensibles y auditoría mejorada
"""

import re
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

class SecureLogger:
    """Logger seguro con máscara de datos sensibles"""
    
    def __init__(self):
        # Configuración desde variables de entorno
        self.mask_sensitive = os.getenv('MASK_SENSITIVE_DATA', 'true').lower() == 'true'
        self.enable_audit = os.getenv('ENABLE_AUDIT_LOG', 'true').lower() == 'true'
        self.log_retention_days = int(os.getenv('LOG_RETENTION_DAYS', '30'))
        
        # Patrones para máscara de datos sensibles
        self.rut_pattern = re.compile(r'\b\d{1,2}[.\d]{3}[.\d]{3}[-][0-9Kk]\b')
        self.name_pattern = re.compile(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b')
        self.folio_pattern = re.compile(r'\b\d{7,8}\b')
        
        # Directorio de logs seguros
        self.secure_log_dir = Path(__file__).parent.parent.parent / "Logs" / "Secure"
        self.secure_log_dir.mkdir(exist_ok=True)
        
        # Archivo de auditoría
        self.audit_file = self.secure_log_dir / "audit.log"
    
    def mask_sensitive_data(self, message: str) -> str:
        """Aplica máscara a datos sensibles en el mensaje"""
        if not self.mask_sensitive:
            return message
        
        # Máscara de RUT (mantener formato, ocultar dígitos)
        def mask_rut(match):
            rut = match.group()
            return f"{rut[0]}***-{rut[-1]}"
        
        # Máscara de nombres (mantener inicial)
        def mask_name(match):
            name = match.group()
            return f"{name[0]}***"
        
        # Máscara de folios (ocultar completamente)
        def mask_folio(match):
            return "***FOLIO***"
        
        # Aplicar máscaras
        message = self.rut_pattern.sub(mask_rut, message)
        message = self.name_pattern.sub(mask_name, message)
        message = self.folio_pattern.sub(mask_folio, message)
        
        return message
    
    def log_audit_event(self, event_type: str, details: dict, user: str = "system"):
        """Registra evento de auditoría"""
        if not self.enable_audit:
            return
        
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user": user,
            "details": details,
            "session_hash": self._get_session_hash()
        }
        
        try:
            with open(self.audit_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(audit_entry, ensure_ascii=False) + "\n")
        except Exception:
            pass  # Silencioso para no interrumpir operación
    
    def _get_session_hash(self) -> str:
        """Genera hash de sesión para auditoría"""
        session_data = f"{datetime.now().date()}-{os.getenv('COMPUTERNAME', 'unknown')}"
        return hashlib.sha256(session_data.encode()).hexdigest()[:16]
    
    def cleanup_old_logs(self):
        """Limpia logs antiguos según política de retención"""
        try:
            cutoff_date = datetime.now().timestamp() - (self.log_retention_days * 24 * 3600)
            
            for log_file in self.secure_log_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_date:
                    log_file.unlink()
        except Exception:
            pass

# Instancia global del logger seguro
secure_logger = SecureLogger()

# Funciones de compatibilidad para integración con DebugSystem existente
def secure_log(message: str, level: str = "INFO") -> str:
    """Aplica seguridad a mensaje de log"""
    masked_message = secure_logger.mask_sensitive_data(message)
    
    # Registrar evento de auditoría para niveles críticos
    if level in ["ERROR", "CRITICAL"]:
        secure_logger.log_audit_event(f"LOG_{level}", {"message": masked_message})
    
    return masked_message

def mask_rut(rut: str) -> str:
    """Máscara específica para RUT"""
    if len(rut) >= 9:
        return f"{rut[0]}***-{rut[-1]}"
    return "***"

def mask_name(name: str) -> str:
    """Máscara específica para nombres"""
    if len(name) > 3:
        return f"{name[0]}***"
    return "***"

# Integración con sistema de logging existente
def enhance_debug_system():
    """Función para mejorar el DebugSystem existente"""
    try:
        # Importar el sistema existente
        import sys
        from pathlib import Path
        
        # Agregar el módulo actual al path
        current_dir = Path(__file__).parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
        
        # Patch para funciones de logging existentes
        original_print = print
        
        def secure_print(*args, **kwargs):
            """Print seguro con máscara de datos"""
            if args:
                masked_args = []
                for arg in args:
                    if isinstance(arg, str):
                        masked_args.append(secure_logger.mask_sensitive_data(arg))
                    else:
                        masked_args.append(arg)
                original_print(*masked_args, **kwargs)
            else:
                original_print(*args, **kwargs)
        
        # Reemplazar print global (opcional, solo si se desea)
        # print = secure_print
        
        return True
    except Exception:
        return False