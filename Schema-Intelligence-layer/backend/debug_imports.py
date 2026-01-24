# debug_imports.py
import sys
from pathlib import Path
import traceback

# Add the backend directory to the path, similar to how Uvicorn runs
# This assumes the script is saved in D:\ashween\Schema-Intelligence-layer\backend
sys.path.insert(0, str(Path(__file__).parent))

print("--- Starting Import Debugger ---")

def import_router(name, path):
    print(f"\nAttempting to import '{name}'...")
    try:
        __import__(path, fromlist=[name])
        print(f"✅ SUCCESS: Imported '{name}'.")
        return True
    except Exception as e:
        print(f"❌ FAILED to import '{name}'.")
        print(f"   ERROR TYPE: {type(e).__name__}")
        print(f"   ERROR DETAILS: {e}")
        print("\n--- Full Traceback ---")
        traceback.print_exc()
        print("----------------------\n")
        return False

# Mimic the imports from main.py
import_router("metadata_router", "app.modules.metadata_generator.router")
import_router("mapping_router", "app.modules.mapping.router")
import_router("nl2sql_router", "app.nl2sql.router")

print("\n--- Debug Script Finished ---")

