# src/core/error_policy.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from enum import Enum, auto
from typing import Any, Optional
from selenium.common.exceptions import (
    TimeoutException, 
    StaleElementReferenceException, 
    NoSuchWindowException, 
    WebDriverException,
    NoSuchElementException
)
from src.utils.errors import (
    NozhgessError, 
    DOMError, 
    BrowserDeadError, 
    AuthError
)

class ErrorAction(Enum):
    RETRY = auto()      # Transient error, try again
    FAIL = auto()       # Fatal error, abort patient/mission
    HEAL = auto()       # Browser dead, attempt self-healing
    LOGONLY = auto()    # Non-critical, just log it

def classify_exception(e: Exception) -> ErrorAction:
    """
    Classifies an exception into a standard action.
    This centralized policy avoids 'swallowing' important bugs.
    """
    # 1. Browser Dead / Connection Lost
    if isinstance(e, (NoSuchWindowException, ConnectionError)):
        return ErrorAction.HEAL
    
    # 2. WebDriver failures that might be connection related
    if isinstance(e, WebDriverException):
        msg = str(e).lower()
        if "cannot connect" in msg or "no such window" in msg:
            return ErrorAction.HEAL
        return ErrorAction.RETRY # Transient driver glitch
        
    # 3. DOM Errors (Transient)
    if isinstance(e, (StaleElementReferenceException, TimeoutException, NoSuchElementException)):
        return ErrorAction.RETRY
        
    # 4. Auth Errors
    if isinstance(e, AuthError):
        return ErrorAction.FAIL # Don't infinite-retry login if it fails explicitly
        
    # 5. Base Nozhgess Errors
    if isinstance(e, NozhgessError):
        # Default to fail-fast for specialized errors unless specified
        return ErrorAction.FAIL
        
    # 6. Fallback
    return ErrorAction.FAIL
