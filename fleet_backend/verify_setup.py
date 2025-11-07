"""
SETUP VERIFICATION SCRIPT
========================

Run this script to verify your environment is set up correctly
before starting the Fleet Management System.
"""

import sys
import importlib
import subprocess
from pathlib import Path

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def check_python_version():
    """Check Python version."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.9+)")
        return False

def check_module(module_name):
    """Check if a module is installed."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    print("\nChecking dependencies...")
    
    required = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'sqlalchemy': 'SQLAlchemy',
        'pydantic': 'Pydantic',
        'sklearn': 'scikit-learn',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'requests': 'Requests',
        'joblib': 'Joblib'
    }
    
    all_installed = True
    for module, name in required.items():
        if check_module(module):
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name} (MISSING)")
            all_installed = False
    
    return all_installed

def check_project_structure():
    """Check if project structure is correct."""
    print("\nChecking project structure...")
    
    required_paths = [
        'app',
        'app/main.py',
        'app/database.py',
        'app/models.py',
        'app/schemas.py',
        'app/ml',
        'app/ml/loader.py',
        'app/ml/utils.py',
        'app/routers',
        'app/routers/vehicles.py',
        'app/routers/sensor.py',
        'app/routers/predictions.py',
        'app/routers/tasks.py',
        'app/routers/maintenance.py',
        'app/routers/auth.py',
        'app/services',
        'app/services/predictions.py',
        'app/services/sensor_processing.py',
        'mock_sensor.py',
        'requirements.txt',
        'README.md'
    ]
    
    all_exist = True
    for path in required_paths:
        full_path = Path(path)
        if full_path.exists():
            print(f"  ✓ {path}")
        else:
            print(f"  ✗ {path} (MISSING)")
            all_exist = False
    
    return all_exist

def check_ml_models():
    """Check if ML models exist."""
    print("\nChecking ML models...")
    
    models_dir = Path(__file__).parent.parent / 'models'
    model_files = ['full_rf.pkl', 'full_lr.pkl', 'iso.pkl']
    
    all_exist = True
    for model_file in model_files:
        model_path = models_dir / model_file
        if model_path.exists():
            print(f"  ✓ {model_file}")
        else:
            print(f"  ⚠ {model_file} (NOT FOUND)")
            all_exist = False
    
    if not all_exist:
        print("\n  Note: System will work without models but predictions will be defaults")
    
    return True  # Don't fail setup if models missing

def check_port_availability():
    """Check if port 8000 is available."""
    print("\nChecking port availability...")
    
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8000))
    sock.close()
    
    if result == 0:
        print("  ⚠ Port 8000 is already in use")
        print("    You may need to stop the running service or use a different port")
        return False
    else:
        print("  ✓ Port 8000 is available")
        return True

def main():
    """Run all checks."""
    print_header("FLEET MANAGEMENT SYSTEM - SETUP VERIFICATION")
    
    checks = []
    
    # Python version
    checks.append(("Python Version", check_python_version()))
    
    # Dependencies
    checks.append(("Dependencies", check_dependencies()))
    
    # Project structure
    checks.append(("Project Structure", check_project_structure()))
    
    # ML models
    checks.append(("ML Models", check_ml_models()))
    
    # Port availability
    checks.append(("Port 8000", check_port_availability()))
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for check_name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {check_name}")
    
    print(f"\n{'='*70}")
    print(f"  Results: {passed}/{total} checks passed")
    print(f"{'='*70}\n")
    
    if passed == total:
        print("🎉 All checks passed! You're ready to start the system.")
        print("\nNext steps:")
        print("  1. uvicorn app.main:app --reload")
        print("  2. python mock_sensor.py (in a new terminal)")
        print("  3. Open http://localhost:8000/docs")
    else:
        print("⚠ Some checks failed. Please fix the issues above.")
        
        if not checks[1][1]:  # Dependencies failed
            print("\nTo install dependencies:")
            print("  pip install -r requirements.txt")

if __name__ == "__main__":
    main()
