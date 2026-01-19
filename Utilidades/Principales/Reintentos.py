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
from Utilidades.Principales.Terminal import log_error, log_info, log_warn


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

class CircuitState(Enum):
    """Estados del circuit breaker."""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"           # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreaker:
    """
    Implementa circuit breaker pattern para prevenir cascade failures.
    
    Estados:
    - CLOSED: Operación normal, permite requests
    - OPEN: Detectó muchos fallos, rechaza requests inmediatamente
    - HALF_OPEN: Probando si el servicio se recuperó
    
    Inspirado en Resilience4j y Hystrix.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        success_threshold: int = 2
    ):
        """
        Args:
            failure_threshold: Fallos consecutivos para abrir circuito
            recovery_timeout: Segundos antes de probar recovery
            success_threshold: Éxitos en HALF_OPEN para cerrar
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Ejecuta función a través del circuit breaker.
        
        Args:
            func: Función a ejecutar
            *args, **kwargs: Argumentos para la función
        
        Returns:
            Resultado de la función
        
        Raises:
            Exception: Si circuit está OPEN o función falla
        """
        # Si está OPEN, verificar si es tiempo de probar recovery
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                log_info("🔄 Circuit breaker: OPEN → HALF_OPEN (probando recovery)")
            else:
                raise Exception(
                    f"Circuit breaker OPEN - "
                    f"próximo intento en {self._time_until_retry():.0f}s"
                )
        
        # Intentar ejecutar
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Callback de éxito."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self._close_circuit()
        else:
            # Reset counters en estado normal
            self.failure_count = 0
            self.success_count = 0
    
    def _on_failure(self):
        """Callback de fallo."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            # Un fallo en HALF_OPEN vuelve a OPEN
            self._open_circuit()
        elif self.failure_count >= self.failure_threshold:
            # Muchos fallos en CLOSED pasan a OPEN
            self._open_circuit()
    
    def _open_circuit(self):
        """Abre el circuito."""
        self.state = CircuitState.OPEN
        log_warn(
            f"⚠️ Circuit breaker ABIERTO - "
            f"{self.failure_count} fallos detectados"
        )
    
    def _close_circuit(self):
        """Cierra el circuito."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        log_info("✅ Circuit breaker CERRADO - servicio recuperado")
    
    def _should_attempt_reset(self) -> bool:
        """Verifica si es tiempo de intentar recovery."""
        if not self.last_failure_time:
            return True
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout
    
    def _time_until_retry(self) -> float:
        """Segundos hasta el próximo intento."""
        if not self.last_failure_time:
            return 0
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return max(0, self.recovery_timeout - elapsed)


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
                    # Si hay circuit breaker, ejecutar a través de él
                    if circuit_breaker:
                        return circuit_breaker.call(func, *args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                        
                except Exception as e:
                    last_exception = e
                    
                    # Clasificar error
                    category = ErrorClassifier.classify(e)
                    
                    # Verificar si debemos detener
                    if stop_on and stop_on(e):
                        log_warn(f"⏹️ Deteniendo reintentos: {str(e)[:50]}")
                        raise
                    
                    # No reintentar errores permanentes
                    if category == ErrorCategory.PERMANENT:
                        log_error(f"❌ Error permanente: {str(e)[:50]}")
                        raise
                    
                    # Si es el último intento, no esperar
                    if attempt >= max_attempts:
                        log_error(
                            f"❌ Falló después de {max_attempts} intentos: "
                            f"{str(e)[:50]}"
                        )
                        break
                    
                    # Calcular delay
                    delay = backoff.next_delay(attempt - 1)
                    
                    # Logging
                    log_warn(
                        f"⚠️ Intento {attempt}/{max_attempts} falló "
                        f"({category.value}): {str(e)[:50]}"
                    )
                    log_info(f"🔄 Reintentando en {delay:.1f}s...")
                    
                    # Callback si existe
                    if on_exception:
                        try:
                            on_exception(attempt, e)
                        except Exception:
                            pass  # No fallar por callback
                    
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
