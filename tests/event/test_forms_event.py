"""Tests for event/forms.py with proper imports and structure."""

from datetime import UTC, datetime

import pytest

from app.event.forms import EditItemsForm, ItemsForm


def test_items_form_validation(app):
    """Test basic validation of the items form."""
    # Create a valid form
    with app.app_context():
        form_data = {
            "name": "Test Item",
            "notes": "This is a test note",
            "recipients": "test@example.com",
            "schedule_time": datetime.now(UTC),
        }

        form = ItemsForm(data=form_data, meta={"csrf": False})
        assert form.validate() is True


def test_items_form_missing_name(app):
    """Test ItemsForm with missing name."""
    with app.app_context():
        form = ItemsForm(data={"name": "", "notes": "Test Notes"})  # Empty name
        assert form.validate() is False
        assert "This field is required." in form.name.errors


def test_items_form_name_too_long(app):
    """Test ItemsForm with name too long."""
    with app.app_context():
        form = ItemsForm(
            data={
                "name": "x" * 255,  # 255 chars, max is 254
                "notes": "Test Notes",
            }
        )
        assert form.validate() is False
        assert "Field must be between 1 and 254 characters long." in form.name.errors


def test_edit_items_form_valid(app):
    """Test EditItemsForm with valid data."""
    with app.app_context():
        form = EditItemsForm(
            data={
                "name": "Test Item",
                "notes": "Test Notes",
                "recipients": "test@example.com",
                "schedule_time": datetime.now(UTC),
            },
            meta={"csrf": False},
        )
        assert form.validate() is True


def test_edit_items_form_missing_name(app):
    """Test EditItemsForm with missing name."""
    with app.app_context():
        form = EditItemsForm(data={"name": "", "notes": "Test Notes"})  # Empty name
        assert form.validate() is False
        assert "This field is required." in form.name.errors


def test_edit_items_form_name_too_long(app):
    """Test EditItemsForm with name too long."""
    with app.app_context():
        form = EditItemsForm(
            data={
                "name": "x" * 255,  # 255 chars, max is 254
                "notes": "Test Notes",
            }
        )
        assert form.validate() is False
        assert "Field must be between 1 and 254 characters long." in form.name.errors
