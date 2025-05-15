#!/usr/bin/env python
# Print path information
import sys

print("Python path:", sys.path)
print("Python version:", sys.version)

# Try import
try:
    from app import config, create_app

    print("Imports successful!")

    # Create app
    app = create_app(config.TestingConfig)
    print("App created successfully!")

    # Print routes
    print("Available routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule}")
except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
