#!/usr/bin/env python3
"""Script to run tests with proper import mechanisms."""
import os
import sys
import pytest

# Ensure the current directory is in sys.path
sys.path.insert(0, os.getcwd())

# Run the tests
if __name__ == "__main__":
    # Run all tests with coverage reporting
    # Adding specific tests that focus on modules with low coverage
    sys.exit(pytest.main([
        "--cov=app",
        "--cov-report=term-missing",
        "tests/test_app_init_enhanced.py",        # Enhanced app init tests
        "tests/event/test_views.py",              # View tests
        "tests/event/test_jobs_comprehensive.py",  # Comprehensive jobs tests
        "tests/event/test_forms_validators.py",   # Forms validator tests
        "tests"                                   # Run all remaining tests
    ]))
