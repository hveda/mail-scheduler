"""Comprehensive tests for app/__init__.py."""
import pytest
from unittest.mock import patch, MagicMock
import os

from app import create_app, register_blueprints, register_extensions, register_commands
from app import config


def test_create_app_with_testing_config():
    """Test creating an app with testing configuration."""
    app = create_app(config.TestingConfig)
    assert app.config['TESTING'] is True
    assert app.config['DEBUG'] is True
    assert app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite://')


def test_create_app_with_development_config():
    """Test creating an app with development configuration."""
    app = create_app(config.DevelopmentConfig)
    assert app.config['DEBUG'] is True
    assert app.config['TESTING'] is False


def test_create_app_with_production_config():
    """Test creating an app with production configuration."""
    app = create_app(config.ProductionConfig)
    assert app.config['DEBUG'] is False
    assert app.config['TESTING'] is False


@patch('app.register_extensions')
@patch('app.register_blueprints')
@patch('app.register_commands')
def test_create_app_calls_register_functions(mock_commands, mock_blueprints, mock_extensions):
    """Test that create_app calls all the register functions."""
    app = create_app(config.TestingConfig)

    # Check each registration function was called once with the app
    mock_extensions.assert_called_once_with(app)
    mock_blueprints.assert_called_once_with(app)
    mock_commands.assert_called_once_with(app)


def test_register_blueprints():
    """Test registering blueprints."""
    # Create a mock Flask app
    mock_app = MagicMock()
    mock_app.register_blueprint = MagicMock()

    # Call the function
    result = register_blueprints(mock_app)

    # Check that register_blueprint was called with the API blueprint
    assert mock_app.register_blueprint.called
    assert mock_app.register_blueprint.call_count == 1

    # Check that the result is None
    assert result is None


def test_register_extensions():
    """Test registering extensions."""
    # Create a mock Flask app
    mock_app = MagicMock()

    # Create mock extensions
    mock_db = MagicMock()
    mock_mail = MagicMock()
    mock_migrate = MagicMock()
    mock_rq = MagicMock()

    # Patch the extensions
    with patch('app.db', mock_db), \
            patch('app.mail', mock_mail), \
            patch('app.migrate', mock_migrate), \
            patch('app.rq', mock_rq):
        # Call the function
        register_extensions(mock_app)

    # Check that init_app was called on each extension
    mock_db.init_app.assert_called_once_with(mock_app)
    mock_mail.init_app.assert_called_once_with(mock_app)
    mock_migrate.init_app.assert_called_once_with(mock_app, mock_db)
    mock_rq.init_app.assert_called_once_with(mock_app)


def test_register_commands():
    """Test registering CLI commands."""
    # Create a mock Flask app
    mock_app = MagicMock()
    mock_cli = MagicMock()
    mock_app.cli.command.return_value = lambda x: x
    mock_app.cli = mock_cli

    # Mock command functions
    mock_create_db = MagicMock()
    mock_drop_db = MagicMock()
    mock_recreate_db = MagicMock()

    # Patch the commands
    with patch('app.create_db', mock_create_db), \
            patch('app.drop_db', mock_drop_db), \
            patch('app.recreate_db', mock_recreate_db):
        # Call the function
        register_commands(mock_app)

    # Check that command was called for each command function
    assert mock_app.cli.command.call_count == 3
