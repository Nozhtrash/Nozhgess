# -*- coding: utf-8 -*-
"""
Sistema Moderno de Reintentos - NOZHGESS v1.0
============================================

Sistema profesional de reintentos con:
- Circuit Breaker pattern
- Backoff exponencial con jitter
- Clasificación inteligente de errores
- Métricas y observabilidad
- Self-healing

Principios de diseño:
- Fail fast en errores permanentes
- Retry smart en errores transientes
- Prevenir cascading failures
- Observable y debuggeable
"""
# Standard library
import functools
import random
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type

# Local
from src.utils.Terminal import log_error, log_info, log_warn
from src.core.error_policy import classify_exception, ErrorAction


# =============================================================================
# CLASIFICACIÓN DE ERRORES
# =============================================================================

class ErrorCategory(Enum):
    """Categorías de errores para decisiones de retry."""
    TRANSIENT = "transient"      # Vale la pena reintentar
    PERMANENT = "permanent"      # No vale la pena reintentar
    RATE_LIMIT = "rate_limit"   # Backoff más largo
    TIMEOUT = "timeout"          # Aumentar timeout
    UNKNOWN = "unknown"          # Precaución


class ErrorClassifier:
    """
    Clasifica errores para decisiones inteligentes de retry.
    
    Basado en mejores prácticas de la industria (Google SRE, AWS, etc.)
    """
    
    # Errores transientes - reintentar con backoff
    TRANSIENT_ERRORS = {
        'TimeoutException',
        'StaleElementReferenceException',
        'ElementNotInteractableException',
        'ElementClickInterceptedException',
    }
    
    # Errores permanentes - fallar inmediatamente
    PERMANENT_ERRORS = {
        'ValueError',
        'TypeError',
        'KeyError',
        'AttributeError',
        'FileNotFoundError',
    }
    
    # Errores de timeout - aumentar timeout
    TIMEOUT_ERRORS = {
        'TimeoutException',
        'ReadTimeout',
        'ConnectionTimeout',
    }
    
    @classmethod
    def classify(cls, error: Exception) -> ErrorCategory:
        """
        Clasifica un error en una categoría.
        
        Args:
            error: Excepción a clasificar
        
        Returns:
            Categoría del error
        """
        error_name = type(error).__name__
        
        if error_name in cls.TRANSIENT_ERRORS:
            return ErrorCategory.TRANSIENT
        elif error_name in cls.PERMANENT_ERRORS:
            return ErrorCategory.PERMANENT
        elif error_name in cls.TIMEOUT_ERRORS:
            return ErrorCategory.TIMEOUT
        else:
            return ErrorCategory.UNKNOWN


# =============================================================================
# ESTRATEGIAS DE BACKOFF
# =============================================================================

class BackoffStrategy:
    """Estrategia base de backoff."""
    
    def next_delay(self, attempt: int) -> float:
        """Calcula delay para el próximo intento."""
        raise NotImplementedError


class ExponentialBackoff(BackoffStrategy):
    """
    Backoff exponencial con jitter.
    
    Delay = min(base * (2 ** attempt) + jitter, max_delay)
    
    Jitter previene "thundering herd" problem cuando múltiples
    clientes reintentan simultáneamente.
    """
    
    def __init__(
        self,
        base: float = 0.5,
        max_delay: float = 60.0,
        jitter: bool = True
    ):
        self.base = base
        self.max_delay = max_delay
        self.jitter = jitter
    
    def next_delay(self, attempt: int) -> float:
        """Calcula delay exponencial con jitter opcional."""
        delay = self.base * (2 ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Agregar jitter aleatorio ±25%
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
            delay = max(0, delay)  # No negativo
        
        return delay


class LinearBackoff(BackoffStrategy):
    """Backoff lineal simple."""
    
    def __init__(self, increment: float = 1.0, max_delay: float = 10.0):
        self.increment = increment
        self.max_delay = max_delay
    
    def next_delay(self, attempt: int) -> float:
        return min(self.increment * attempt, self.max_delay)


# =============================================================================
# CIRCUIT BREAKER
# =============================================================================

class CircuitOpenError(Exception):
    """Lanzado cuando el circuito está abierto y se bloquea la llamada."""
    pass


class CircuitState(Enum):
    """Estados del circuit breaker."""
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    """
    Implementa circuit breaker pattern para prevenir cascade failures.
    
    Estados:
    - CLOSED: Operación normal, permite requests.
    - OPEN: Detectó muchos fallos, rechaza requests inmediatamente.
    - HALF_OPEN: Probando si el servicio se recuperó.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None

    def before_call(self):
        """
        Llamado antes de ejecutar la función.
        Lanza CircuitOpenError si el circuito está abierto y no ha expirado el timeout.
        """
        if self.state == CircuitState.OPEN:
            elapsed = time.time() - (self.last_failure_time or 0)
            if elapsed > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                log_info("🔄 Circuit Breaker: OPEN → HALF_OPEN (Probando recuperación)")
            else:
                raise CircuitOpenError(f"Circuito ABIERTO. Reintento disponible en {int(self.recovery_timeout - elapsed)}s")

    def record_success(self):
        """Llamado cuando la operación es exitosa."""
        if self.state != CircuitState.CLOSED:
            log_info("✅ Circuit Breaker: CERRADO (Servicio recuperado)")
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def record_failure(self):
        """Llamado cuando la operación falla."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN or self.failure_count >= self.failure_threshold:
            if self.state != CircuitState.OPEN:
                log_warn(f"⚠️ Circuit Breaker: ABIERTO ({self.failure_count} fallos consecutivos)")
            self.state = CircuitState.OPEN


# =============================================================================
# DECORADOR DE RETRY MODERNO
# =============================================================================

def retry(
    max_attempts: int = 3,
    backoff: Optional[BackoffStrategy] = None,
    on_exception: Optional[Callable[[int, Exception], None]] = None,
    stop_on: Optional[Callable[[Exception], bool]] = None,
    circuit_breaker: Optional[CircuitBreaker] = None
):
    """
    Decorador moderno de retry con todas las características.
    
    Args:
        max_attempts: Número máximo de intentos
        backoff: Estrategia de backoff (default: exponencial)
        on_exception: Callback ejecutado en cada error
        stop_on: Función que determina si detener reintentos
        circuit_breaker: Circuit breaker opcional
    
    Example:
        >>> @retry(
        >>>     max_attempts=5,
        >>>     backoff=ExponentialBackoff(base=1.0, max_delay=30),
        >>>     stop_on=lambda e: isinstance(e, ValueError)
        >>> )
        >>> def operacion_critica():
        >>>     # código que puede fallar
        >>>     pass
    """
    if backoff is None:
        backoff = ExponentialBackoff()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    # Antes de llamar: verificar circuito
                    if circuit_breaker:
                        circuit_breaker.before_call()
                    
                    result = func(*args, **kwargs)
                    
                    # Si tuvo éxito: registrar en circuito
                    if circuit_breaker:
                        circuit_breaker.record_success()
                    return result
                        
                except CircuitOpenError as e:
                    # Si el circuito está abierto, fallamos rápido sin quemar intentos
                    log_warn(f"🛑 Circuit Breaker bloqueó llamada: {e}")
                    raise
                except Exception as e:
                    last_exception = e
                    
                    # Registrar fallo en circuito
                    if circuit_breaker:
                        circuit_breaker.record_failure()
                    
                    # Clasificar error usando la política centralizada
                    action = classify_exception(e)
                    
                    # Verificar si debemos detener (override explícito)
                    if stop_on and stop_on(e):
                        log_warn(f"⏹️ Deteniendo reintentos (stop_on): {str(e)[:50]}")
                        raise
                    
                    # Acción: FAIL o HEAL (HEAL se propaga para que el orquestador lo maneje)
                    if action == ErrorAction.FAIL:
                        log_error(f"❌ Error fatal: {str(e)[:50]}")
                        raise
                    
                    if action == ErrorAction.HEAL:
                        log_warn(f"🩹 Se requiere Self-Healing: {str(e)[:50]}")
                        # Propagamos para que el orquestador detecte la necesidad de reinicio
                        raise
                    
                    # Si es el último intento, no esperar
                    if attempt >= max_attempts:
                        log_error(
                            f"❌ Agotados {max_attempts} intentos: "
                            f"{str(e)[:50]}"
                        )
                        break
                    
                    # Calcular delay
                    delay = backoff.next_delay(attempt - 1)
                    
                    # Logging
                    log_warn(
                        f"⚠️ Intento {attempt}/{max_attempts} falló "
                        f"(RETRY): {str(e)[:50]}"
                    )
                    log_info(f"🔄 Reintentando en {delay:.1f}s...")
                    
                    # Callback si existe
                    if on_exception:
                        try:
                            on_exception(attempt, e)
                        except Exception:
                            pass 
                    
                    # Esperar antes de reintentar
                    time.sleep(delay)
            
            # Todos los intentos fallaron
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator


# =============================================================================
# INSTANCIAS GLOBALES
# =============================================================================

# Circuit breaker global para operaciones de Selenium
selenium_circuit = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60.0,
    success_threshold=2
)

# Backoff predeterminado
default_backoff = ExponentialBackoff(base=0.5, max_delay=30.0, jitter=True)
