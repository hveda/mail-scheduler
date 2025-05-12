#!/usr/bin/env python
"""A simple test file to verify pytest is working."""


def test_simple():
    """A simple test that should always pass."""
    assert True


def test_with_print():
    """A test that includes print statements."""
    print("This is a test output")
    assert 1 + 1 == 2
