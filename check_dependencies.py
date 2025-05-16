#!/usr/bin/env python3
"""
Verify that the dependencies for the mail-scheduler project are correctly resolved.
"""
import importlib
import sys
import pkg_resources

def check_dependency(name):
    """Check if a dependency is installed and print its version."""
    try:
        module = importlib.import_module(name)
        version = pkg_resources.get_distribution(name).version
        print(f"\033[92m✓ {name} is installed (version {version})\033[0m")
        return True
    except (ImportError, pkg_resources.DistributionNotFound):
        print(f"\033[91m✗ {name} is not installed\033[0m")
        return False

def check_dependency_compatibility():
    """Check if the key dependencies are compatible."""
    dependencies = {
        'flask': None,
        'werkzeug': None,
        'flask_restx': None
    }
    
    # Get versions
    for dep in dependencies:
        try:
            version = pkg_resources.get_distribution(dep).version
            dependencies[dep] = version
        except pkg_resources.DistributionNotFound:
            dependencies[dep] = None
    
    # Check compatibility
    if all(v is not None for v in dependencies.values()):
        werkzeug_version = dependencies['werkzeug']
        print(f"\nChecking compatibility:")
        
        # Check Flask-RestX requirement for Werkzeug
        werkzeug_major = int(werkzeug_version.split('.')[0])
        if werkzeug_major >= 3:
            print(f"\033[91m✗ Incompatible: flask-restx requires Werkzeug<3.0.0, but {werkzeug_version} is installed\033[0m")
        else:
            print(f"\033[92m✓ Compatible: flask-restx works with Werkzeug {werkzeug_version}\033[0m")
        
        # Print summary
        print(f"\nInstalled versions:")
        print(f"  - Flask: {dependencies['flask']}")
        print(f"  - Werkzeug: {dependencies['werkzeug']}")
        print(f"  - Flask-RestX: {dependencies['flask_restx']}")

if __name__ == "__main__":
    print("Checking mail-scheduler dependencies...\n")
    
    check_dependency('flask')
    check_dependency('werkzeug')
    check_dependency('flask_restx')
    check_dependency('flask_sqlalchemy')
    check_dependency('flask_login')
    
    check_dependency_compatibility()
