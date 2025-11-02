#!/usr/bin/env python3
"""
Quick verification script to check if all modules can be imported correctly.
Run this before starting the server to ensure everything is set up properly.
"""

import sys
import importlib.util


def check_module(module_name, friendly_name=None):
    """Check if a module can be imported."""
    friendly = friendly_name or module_name
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            print(f"❌ {friendly} - Module not found")
            return False
        
        # Try to import
        __import__(module_name)
        print(f"✅ {friendly}")
        return True
    except Exception as e:
        print(f"❌ {friendly} - Error: {str(e)}")
        return False


def main():
    print("=" * 60)
    print("Flow Manager - Module Verification")
    print("=" * 60)
    print()
    
    # Check required packages
    print("Checking required packages...")
    packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("pydantic_settings", "Pydantic Settings"),
    ]
    
    all_ok = True
    for package, name in packages:
        if not check_module(package, name):
            all_ok = False
    
    print()
    
    # Check application modules
    print("Checking application modules...")
    app_modules = [
        "app",
        "app.main",
        "app.models",
        "app.models.flow",
        "app.models.execution",
        "app.services",
        "app.services.flow_manager",
        "app.services.task_registry",
        "app.tasks",
        "app.tasks.sample_tasks",
        "app.api",
        "app.api.routes",
        "app.config",
        "app.config.settings",
        "app.utils",
        "app.utils.logger",
    ]
    
    for module in app_modules:
        if not check_module(module):
            all_ok = False
    
    print()
    print("=" * 60)
    
    if all_ok:
        print("✅ All checks passed! Ready to run the server.")
        print()
        print("Start the server with:")
        print("  uvicorn app.main:app --reload")
        print()
        print("Or run the test:")
        print("  python test_flow.py")
        return 0
    else:
        print("❌ Some checks failed. Please review the errors above.")
        print()
        print("Make sure you've installed dependencies:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
