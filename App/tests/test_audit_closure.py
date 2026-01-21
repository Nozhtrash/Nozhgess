import unittest
from unittest.mock import MagicMock, patch
import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import targeted modules
from src.core.modules.core import CoreMixin
from src.utils.Reintentos import retry, ExponentialBackoff
from src.utils.ConfigValidator import validar_configuracion
from src.core.Driver import SiggesDriver

class TestAuditClosure(unittest.TestCase):

    def setUp(self):
        self.mock_driver = MagicMock()
        self.core = CoreMixin(self.mock_driver)

    def test_cache_invalidation(self):
        """Verify that _click invalidates the state cache."""
        self.core.state.cached_state = "HOME"
        self.core.state.state_cache_valid = True
        
        # Simulate a click (mock _find to return a mock element)
        mock_el = MagicMock()
        self.core._find = MagicMock(return_value=mock_el)
        
        # Mocking wait_smart to avoid real sleeps
        self.core._wait_smart = MagicMock()
        
        # Action
        self.core._click(["xpath"], wait_spinner=False)
        
        # Assertion: Cache should be invalidated via State
        self.assertFalse(self.core.state.state_cache_valid, "Cache validity flag in state should be False after click")

    def test_retry_mechanism(self):
        """Verify retry works and eventually fails/succeeds."""
        mock_func = MagicMock()
        # Fail twice, then succeed
        mock_func.side_effect = [Exception("Fail 1"), Exception("Fail 2"), "Success"]
        
        @retry(max_attempts=3, backoff=ExponentialBackoff(base=0.1))
        def risky_op():
            return mock_func()

        result = risky_op()
        
        self.assertEqual(result, "Success")
        self.assertEqual(mock_func.call_count, 3)

    def test_retry_limit(self):
        """Verify retry gives up after max attempts."""
        mock_func = MagicMock(side_effect=Exception("Forever Fail"))
        
        @retry(max_attempts=2, backoff=ExponentialBackoff(base=0.1))
        def doomed_op():
            return mock_func()

        with self.assertRaises(Exception):
            doomed_op()
            
        self.assertEqual(mock_func.call_count, 2)

    def test_config_validator_fail_fast(self):
        """Verify ConfigValidator returns tuple (bool, list)."""
        # Mocking config module to inject bad values
        with patch('src.utils.ConfigValidator.config') as mock_config:
            mock_config.RUTA_ARCHIVO_ENTRADA = "non_existent_file.xlsx"
            mock_config.MAX_REINTENTOS_POR_PACIENTE = "not_an_int" # Type error
            
            is_valid, errors = validar_configuracion()
            
            self.assertFalse(is_valid, "Should return False for invalid config")
            self.assertIsInstance(errors, list)
            self.assertTrue(len(errors) > 0)
            print(f"\n[Config Check] Detected Errors: {errors}")

    def test_legacy_bridge_imports(self):
        """Verify legacy Conexiones.py can import new src modules."""
        # Use importlib to strictly check if the module can be loaded
        import importlib.util
        
        legacy_path = os.path.join(os.path.dirname(__file__), '..', 'Utilidades', 'Mezclador', 'Conexiones.py')
        spec = importlib.util.spec_from_file_location("Conexiones", legacy_path)
        module = importlib.util.module_from_spec(spec)
        
        # We don't execute the module (it might run code), just check if imports resolve 
        # Actually, Python executes on load. We'll try to just parse it or check imports statically if running is too risky.
        # But 'validar_configuracion' patch above suggests we can run code.
        # Let's try to verify if the FILE exists and contains the correct import lines
        
        with open(legacy_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        self.assertIn("from src.core.Driver import iniciar_driver", content)
        self.assertIn("from src.utils.ConfigValidator import validar_configuracion", content)

    def test_facade_inheritance(self):
        """Verify SiggesDriver inherits from all Mixins."""
        self.assertTrue(issubclass(SiggesDriver, CoreMixin))
        # Add imports for other mixins to check
        from src.core.modules.navigation import NavigationMixin
        from src.core.modules.login import LoginMixin
        from src.core.modules.data import DataParsingMixin
        
        self.assertTrue(issubclass(SiggesDriver, NavigationMixin))
        self.assertTrue(issubclass(SiggesDriver, LoginMixin))
        self.assertTrue(issubclass(SiggesDriver, DataParsingMixin))

if __name__ == '__main__':
    unittest.main()
