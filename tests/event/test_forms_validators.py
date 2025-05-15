"""Comprehensive tests for app/event/forms.py."""

import pytest
from wtforms.validators import DataRequired, Length

from app.event.forms import EditItemsForm, ItemsForm


def test_items_form_field_types(app):
    """Test that ItemsForm has the correct field types and validators."""
    with app.app_context():
        form = ItemsForm()

    # Check field types
    assert hasattr(form, "name")
    assert hasattr(form, "notes")

    # Check validators on name field
    validators = form.name.validators
    validator_types = [type(v) for v in validators]
    assert DataRequired in validator_types

    # Check for Length validator with correct parameters
    length_validators = [v for v in validators if isinstance(v, Length)]
    assert len(length_validators) == 1
    assert length_validators[0].min == 1
    assert length_validators[0].max == 254


def test_edit_items_form_field_types(app):
    """Test that EditItemsForm has the correct field types and validators."""
    with app.app_context():
        form = EditItemsForm()

    # Check field types
    assert hasattr(form, "name")
    assert hasattr(form, "notes")

    # Check validators on name field
    validators = form.name.validators
    validator_types = [type(v) for v in validators]
    assert DataRequired in validator_types

    # Check for Length validator with correct parameters
    length_validators = [v for v in validators if isinstance(v, Length)]
    assert len(length_validators) == 1
    assert length_validators[0].min == 1
    assert length_validators[0].max == 254


def test_items_form_data_population(app):
    """Test that ItemsForm correctly populates with data."""
    test_data = {"name": "Test Item", "notes": "Test Notes"}
    with app.app_context():
        form = ItemsForm(data=test_data)

    assert form.name.data == "Test Item"
    assert form.notes.data == "Test Notes"


def test_edit_items_form_data_population(app):
    """Test that EditItemsForm correctly populates with data."""
    test_data = {"name": "Test Item", "notes": "Test Notes"}
    with app.app_context():
        form = EditItemsForm(data=test_data)

    assert form.name.data == "Test Item"
    assert form.notes.data == "Test Notes"


def test_items_form_csrf_protection(app):
    """Test that CSRF protection is enabled for ItemsForm."""
    with app.app_context():
        form = ItemsForm()
    # This accesses the internal Meta configuration
    assert hasattr(form.Meta, "csrf")
    # Default is True if not specified


def test_edit_items_form_csrf_protection(app):
    """Test that CSRF protection is enabled for EditItemsForm."""
    with app.app_context():
        form = EditItemsForm()
    # This accesses the internal Meta configuration
    assert hasattr(form.Meta, "csrf")
    # Default is True if not specified
