#!/usr/bin/env python
"""Test basic imports of the application."""
try:
    from app import config, create_app

    # Use the imports to avoid flake8 warnings
    app = create_app(config.TestingConfig)
    print("Imports successful!")
    print(f"App configuration: TESTING={config.TestingConfig.TESTING}")
except ImportError as e:
    print(f"Import error: {e}")
    import traceback

    traceback.print_exc()
