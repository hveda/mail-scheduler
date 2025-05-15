"""Comprehensive tests for app/__init__.py module."""

import importlib
import os
from unittest.mock import MagicMock, call, patch

import pytest

from app import (
    config,
    create_app,
    register_blueprints,
    register_commands,
    register_extensions,
)


def test_create_app_default_config():
    """Test creating an app with the default config."""
    # The default config should be app.config.Config
    app = create_app()

    # Check that config was properly applied
    assert app.config["DEBUG"] is False
    assert app.config["TESTING"] is False
    assert "SQLALCHEMY_DATABASE_URI" in app.config
    assert app.config["SECRET_KEY"] is not None


def test_create_app_testing_config():
    """Test creating an app with explicit testing config."""
    app = create_app(config.TestingConfig)

    # Check that testing config was properly applied
    assert app.config["TESTING"] is True
    assert app.config["WTF_CSRF_ENABLED"] is False
    assert app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite://")
    assert app.config["RQ_ASYNC"] is False

    # The application should be properly initialized
    assert app.template_folder == "templates"
    # Full path will vary by environment
    assert app.static_folder.endswith("static")


def test_create_app_development_config():
    """Test creating an app with development config."""
    app = create_app(config.DevelopmentConfig)

    # Check that development config was properly applied
    assert app.config["DEBUG"] is True
    assert app.config["TESTING"] is False
    assert app.config["DEVELOPMENT"] is True
    assert app.config["WTF_CSRF_ENABLED"] is False
    # Skip SQLALCHEMY_DATABASE_URI check as it depends on environment


def test_create_app_production_config():
    """Test creating an app with production config."""
    app = create_app(config.ProductionConfig)

    # Check that production config was properly applied
    assert app.config["DEBUG"] is False
    assert app.config["TESTING"] is False
    assert "SQLALCHEMY_DATABASE_URI" in app.config
    # Production environment has standard settings


@patch("app.register_extensions")
@patch("app.register_blueprints")
@patch("app.register_commands")
def test_create_app_registers_components(
    mock_commands, mock_blueprints, mock_extensions
):
    """Test that create_app calls all the registration functions."""
    app = create_app(config.TestingConfig)

    # Check that each registration function was called with the app
    mock_extensions.assert_called_once_with(app)
    mock_blueprints.assert_called_once_with(app)
    mock_commands.assert_called_once_with(app)


def test_register_blueprints_registers_api():
    """Test registering the API blueprint."""
    # Create a mock Flask app
    mock_app = MagicMock()

    # Mock the API blueprint and other blueprints
    mock_api = MagicMock()
    mock_event_blueprint = MagicMock()
    mock_auth_blueprint = MagicMock()

    # Patch the blueprints
    with (
        patch("app.api", mock_api),
        patch("app.event.views.blueprint", mock_event_blueprint),
        patch("app.auth.blueprint", mock_auth_blueprint),
    ):
        # Call the function
        result = register_blueprints(mock_app)

    # Check that register_blueprint was called with the blueprints and correct URL prefixes
    assert mock_app.register_blueprint.call_count == 3
    mock_app.register_blueprint.assert_any_call(mock_api, url_prefix="/api")
    mock_app.register_blueprint.assert_any_call(
        mock_event_blueprint, url_prefix="/items"
    )
    mock_app.register_blueprint.assert_any_call(mock_auth_blueprint, url_prefix="/auth")

    # Check that the function returned None
    assert result is None


def test_register_extensions_initializes_all():
    """Test registering all extensions."""
    # Create a mock Flask app
    mock_app = MagicMock()

    # Create mock extensions
    mock_db = MagicMock()
    mock_mail = MagicMock()
    mock_migrate = MagicMock()
    mock_rq = MagicMock()

    # Patch the extensions
    with (
        patch("app.db", mock_db),
        patch("app.mail", mock_mail),
        patch("app.migrate", mock_migrate),
        patch("app.rq", mock_rq),
    ):
        # Call the function
        register_extensions(mock_app)

    # Check that init_app was called on each extension with correct arguments
    mock_db.init_app.assert_called_once_with(mock_app)
    mock_mail.init_app.assert_called_once_with(mock_app)
    mock_migrate.init_app.assert_called_once_with(mock_app, mock_db)
    mock_rq.init_app.assert_called_once_with(mock_app)


def test_register_commands_adds_all_commands():
    """Test registering CLI commands."""
    # Create a mock Flask app with CLI
    mock_app = MagicMock()

    # Setup mock command decorator
    command_decorator = MagicMock()
    command_decorator.side_effect = lambda x: x  # Return the function unchanged
    mock_app.cli.command.return_value = command_decorator

    # Mock command functions
    mock_create_db = MagicMock(name="create_db")
    mock_drop_db = MagicMock(name="drop_db")
    mock_recreate_db = MagicMock(name="recreate_db")

    # Patch the commands
    with (
        patch("app.create_db", mock_create_db),
        patch("app.drop_db", mock_drop_db),
        patch("app.recreate_db", mock_recreate_db),
    ):
        # Call the function
        register_commands(mock_app)

    # Check that command decorator was used for each command
    assert mock_app.cli.command.call_count == 3

    # Check that each command was registered
    command_decorator.assert_has_calls(
        [call(mock_create_db), call(mock_drop_db), call(mock_recreate_db)],
        any_order=True,
    )


def test_complete_app_initialization():
    """Integration test for complete app initialization."""
    # Create the app
    app = create_app(config.TestingConfig)

    # Check that the app has all expected blueprints
    assert "api" in app.blueprints

    # Check that all routes were registered (get a sample)
    rule_endpoints = [rule.endpoint for rule in app.url_map.iter_rules()]
    assert "api.root" in rule_endpoints

    # Check that CLI commands were registered
    command_names = [command.name for command in app.cli.commands.values()]
    assert "create-db" in command_names
    assert "drop-db" in command_names
    assert "recreate-db" in command_names


def test_app_configuration_environment_vars():
    """Test that app respects environment variables."""
    # Create app with mocked environment variables using patch.dict
    test_env_vars = {
        "SECRET_KEY": "add-your-random-key-here",
        "MAIL_SERVER": "smtp.gmail.com",
        "MAIL_PORT": "587",
    }

    with patch.dict(os.environ, test_env_vars, clear=False):
        # Import config again to pick up the mocked environment variables
        import importlib

        import app.config

        importlib.reload(app.config)

        # Create a fresh config instance that will use our mocked env vars
        test_config = type("TestEnvConfig", (app.config.Config,), {})
        app = create_app(test_config)

    # Check that environment variables were respected
    assert app.config["SECRET_KEY"] == "add-your-random-key-here"
    assert app.config["MAIL_SERVER"] == "smtp.gmail.com"
    assert app.config["MAIL_PORT"] == 587
