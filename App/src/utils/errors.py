# src/utils/errors.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Optional

class NozhgessError(Exception):
    """Base class for all Nozhgess exceptions."""
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.original_exception = original_exception

class ConfigError(NozhgessError):
    """Configuration related errors (missing files, invalid values)."""
    pass

class NavigationError(NozhgessError):
    """Errors during state transitions or navigation."""
    pass

class DOMError(NozhgessError):
    """Errors related to element finding or interaction (Stale, Timeout)."""
    pass

class BrowserDeadError(NozhgessError):
    """Browser window closed or connection lost."""
    pass

class AuthError(NozhgessError):
    """Login failures or session expiration."""
    pass

class DataParsingError(NozhgessError):
    """Errors during table reading or data extraction."""
    pass

class RetryExhaustedError(NozhgessError):
    """Raised when retries are exhausted for an operation."""
    pass
