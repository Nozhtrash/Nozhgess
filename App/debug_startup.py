
import sys
import os
import traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

print("--- DEBUG START ---")
try:
    print("Attempting to import src.gui.app...")
    from src.gui.app import NozhgessApp
    print("Import successful.")
    
    print("Attempting to instantiate NozhgessApp...")
    app = NozhgessApp()
    print("Instantiation successful.")
except Exception:
    print("CRITICAL EXCEPTION:")
    traceback.print_exc()
print("--- DEBUG END ---")
