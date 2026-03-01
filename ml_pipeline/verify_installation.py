"""
Installation Verification Script

This script verifies that all dependencies are correctly installed
and the environment is ready for running the ML pipeline.

Author: ML Engineering Team
Date: February 28, 2026
"""

import sys
import importlib

def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def check_python_version():
    """Check if Python version is compatible."""
    print("\n[1] Checking Python version...")
    version = sys.version_info
    print(f"    Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 10:
        print("    ✓ Python version is compatible (3.10+)")
        return True
    else:
        print("    ✗ Python version is too old. Please upgrade to 3.10+")
        return False

def check_package(package_name, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"    ✓ {package_name:20s} {version}")
        return True
    except ImportError:
        print(f"    ✗ {package_name:20s} NOT INSTALLED")
        return False

def check_core_packages():
    """Check all core ML packages."""
    print("\n[2] Checking core ML packages...")
    
    packages = [
        ('NumPy', 'numpy'),
        ('Pandas', 'pandas'),
        ('scikit-learn', 'sklearn'),
        ('SciPy', 'scipy'),
        ('XGBoost', 'xgboost'),
    ]
    
    results = []
    for name, import_name in packages:
        results.append(check_package(name, import_name))
    
    return all(results)

def check_nlp_packages():
    """Check NLP packages."""
    print("\n[3] Checking NLP packages...")
    
    packages = [
        ('NLTK', 'nltk'),
        ('spaCy', 'spacy'),
    ]
    
    results = []
    for name, import_name in packages:
        results.append(check_package(name, import_name))
    
    # Check NLTK data
    if results[0]:  # If NLTK is installed
        try:
            import nltk
            print("\n    Checking NLTK data...")
            try:
                nltk.data.find('corpora/stopwords')
                print("    ✓ NLTK stopwords installed")
            except LookupError:
                print("    ✗ NLTK stopwords missing (will download automatically)")
            
            try:
                nltk.data.find('corpora/wordnet')
                print("    ✓ NLTK wordnet installed")
            except LookupError:
                print("    ✗ NLTK wordnet missing (will download automatically)")
        except Exception as e:
            print(f"    ⚠ Could not check NLTK data: {e}")
    
    # Check spaCy model
    if results[1]:  # If spaCy is installed
        try:
            import spacy
            print("\n    Checking spaCy models...")
            try:
                spacy.load('en_core_web_sm')
                print("    ✓ spaCy model 'en_core_web_sm' installed")
            except OSError:
                print("    ✗ spaCy model missing")
                print("      Run: python -m spacy download en_core_web_sm")
        except Exception as e:
            print(f"    ⚠ Could not check spaCy model: {e}")
    
    return all(results)

def check_visualization_packages():
    """Check visualization packages."""
    print("\n[4] Checking visualization packages...")
    
    packages = [
        ('Matplotlib', 'matplotlib'),
        ('Seaborn', 'seaborn'),
    ]
    
    results = []
    for name, import_name in packages:
        results.append(check_package(name, import_name))
    
    return all(results)

def check_mlflow():
    """Check MLflow installation."""
    print("\n[5] Checking MLflow...")
    
    result = check_package('MLflow', 'mlflow')
    
    if result:
        import mlflow
        print(f"    Tracking URI: {mlflow.get_tracking_uri()}")
    
    return result

def check_utility_packages():
    """Check utility packages."""
    print("\n[6] Checking utility packages...")
    
    packages = [
        ('Joblib', 'joblib'),
        ('Requests', 'requests'),
    ]
    
    results = []
    for name, import_name in packages:
        results.append(check_package(name, import_name))
    
    return all(results)

def check_project_structure():
    """Check if project structure is correct."""
    print("\n[7] Checking project structure...")
    
    import os
    
    required_dirs = ['src', 'data', 'models', 'artifacts', 'results']
    required_files = [
        'main.py',
        'generate_sample_dataset.py',
        'requirements.txt',
        'src/preprocess.py',
        'src/train.py',
        'src/evaluate.py',
        'src/mlflow_logger.py',
    ]
    
    # Check directories
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"    ✓ Directory '{directory}' exists")
        else:
            print(f"    ⚠ Directory '{directory}' missing (will be created)")
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"      Created directory '{directory}'")
            except Exception as e:
                print(f"      ✗ Could not create directory: {e}")
    
    # Check files
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"    ✓ File '{file}' exists")
        else:
            print(f"    ✗ File '{file}' missing")
            missing_files.append(file)
    
    return len(missing_files) == 0

def test_imports():
    """Test importing project modules."""
    print("\n[8] Testing project module imports...")
    
    sys.path.insert(0, '.')
    
    modules = [
        'src.preprocess',
        'src.train',
        'src.evaluate',
        'src.mlflow_logger',
    ]
    
    results = []
    for module_name in modules:
        try:
            importlib.import_module(module_name)
            print(f"    ✓ {module_name} imported successfully")
            results.append(True)
        except Exception as e:
            print(f"    ✗ {module_name} import failed: {e}")
            results.append(False)
    
    return all(results)

def main():
    """Run all verification checks."""
    print_header("ML PIPELINE - INSTALLATION VERIFICATION")
    
    print("\nThis script will verify that your environment is correctly set up")
    print("for running the Resume Authenticity Detection ML Pipeline.")
    
    checks = [
        ("Python Version", check_python_version),
        ("Core ML Packages", check_core_packages),
        ("NLP Packages", check_nlp_packages),
        ("Visualization Packages", check_visualization_packages),
        ("MLflow", check_mlflow),
        ("Utility Packages", check_utility_packages),
        ("Project Structure", check_project_structure),
        ("Module Imports", test_imports),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n    ERROR during {name}: {e}")
            results.append((name, False))
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    print("\nCheck Results:")
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status:10s} {name}")
        all_passed = all_passed and result
    
    print("\n" + "="*70)
    
    if all_passed:
        print("\n  🎉 ALL CHECKS PASSED! Your environment is ready.")
        print("\n  Next steps:")
        print("    1. Generate sample dataset:")
        print("       python generate_sample_dataset.py")
        print("\n    2. Run the ML pipeline:")
        print("       python main.py --dataset ./data/resume_dataset.csv")
        print("\n    3. View results:")
        print("       mlflow ui")
        print("\n" + "="*70)
        return 0
    else:
        print("\n  ⚠ SOME CHECKS FAILED!")
        print("\n  Please review the errors above and:")
        print("    1. Install missing packages:")
        print("       pip install -r requirements.txt")
        print("\n    2. Download NLTK data:")
        print("       python -c \"import nltk; nltk.download('all')\"")
        print("\n    3. Download spaCy model:")
        print("       python -m spacy download en_core_web_sm")
        print("\n    4. Run this script again to verify:")
        print("       python verify_installation.py")
        print("\n" + "="*70)
        return 1

if __name__ == "__main__":
    exit_code = main()
    
    print("\nPress Enter to exit...")
    input()
    
    sys.exit(exit_code)
