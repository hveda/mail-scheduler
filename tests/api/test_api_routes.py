"""Tests for API routes."""
import pytest
import json
from datetime import datetime, UTC, timedelta
from flask import url_for
from unittest.mock import patch, MagicMock


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200

    # Parse the JSON response
    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert 'timestamp' in data


@patch('app.api.routes.add_event')
def test_save_emails_success(mock_add_event, client):
    """Test successful event submission."""
    # Set up the mock to return an event ID
    mock_add_event.return_value = 123

    # Test data
    data = {
        'subject': 'Test Subject',
        'content': 'Test Content',
        'timestamp': (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
        'recipients': 'test@example.com, another@example.com'
    }

    # Send the request
    response = client.post(
        '/api/save_emails',
        data=json.dumps(data),
        content_type='application/json'
    )

    # Check the response
    assert response.status_code == 201

    # Parse the JSON response
    result = json.loads(response.data)
    assert 'message' in result
    assert 'id' in result
    assert result['id'] == 123

    # Verify the mock was called with the right data
    mock_add_event.assert_called_once_with(data)


@patch('app.api.routes.add_event')
def test_save_emails_validation_error(mock_add_event, client):
    """Test validation error in event submission."""
    # Set up the mock (shouldn't be called)
    mock_add_event.return_value = 123

    # Invalid test data (missing required fields)
    data = {
        'subject': 'Test Subject',
        # Missing 'content'
        'timestamp': (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
        'recipients': 'test@example.com'
    }

    # Send the request
    response = client.post(
        '/api/save_emails',
        data=json.dumps(data),
        content_type='application/json'
    )

    # Check the response (should be validation error)
    assert response.status_code == 400

    # Verify the mock was not called
    assert not mock_add_event.called


@patch('app.api.routes.add_event')
def test_save_emails_exception(mock_add_event, client):
    """Test exception handling in event submission."""
    # Set up the mock to raise an exception
    mock_add_event.side_effect = Exception('Test error')

    # Test data
    data = {
        'subject': 'Test Subject',
        'content': 'Test Content',
        'timestamp': (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
        'recipients': 'test@example.com'
    }

    # Send the request
    response = client.post(
        '/api/save_emails',
        data=json.dumps(data),
        content_type='application/json'
    )

    # Check the response (should include the error message)
    assert response.status_code == 400

    # Parse the JSON response
    result = json.loads(response.data)
    assert 'message' in result
    assert 'Test error' in result['message']
