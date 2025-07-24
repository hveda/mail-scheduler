"""Tests for API routes."""
import pytest
import json
from unittest.mock import patch
from datetime import datetime, UTC

from app.api.routes import ns


def test_namespace_exists():
    """Test that the namespace exists and is correctly configured."""
    assert ns is not None
    assert ns.name == 'Event'
    assert ns.description == 'Event submission'
    assert ns.path == '/'


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/api/health')
    
    # Verify response
    assert response.status_code == 200
    
    # Parse JSON response
    data = json.loads(response.data)
    
    # Verify data
    assert 'status' in data
    assert data['status'] == 'ok'
    assert 'timestamp' in data
    
    # Verify timestamp is a valid ISO format
    try:
        datetime.fromisoformat(data['timestamp'])
    except ValueError:
        pytest.fail("Timestamp is not a valid ISO format")


@patch('app.api.routes.add_event')
def test_save_emails_endpoint_success(mock_add_event, client):
    """Test the save_emails endpoint (success case)."""
    # Setup mock to return event ID
    mock_add_event.return_value = 1
    
    # Test data
    payload = {
        'subject': 'Test Subject',
        'content': 'Test Content',
        'timestamp': datetime.now(UTC).isoformat(),
        'recipients': 'test@example.com'
    }
    
    # Call endpoint
    response = client.post('/api/save_emails', 
                          data=json.dumps(payload),
                          content_type='application/json')
    
    # Verify response
    assert response.status_code == 201
    
    # Parse JSON response
    data = json.loads(response.data)
    
    # Verify data
    assert 'message' in data
    assert 'id' in data
    assert data['id'] == 1
    
    # Verify add_event was called with correct data
    mock_add_event.assert_called_once_with(payload)


@patch('app.api.routes.add_event')
def test_save_emails_endpoint_error(mock_add_event, client):
    """Test the save_emails endpoint (error case)."""
    # Setup mock to raise exception
    mock_add_event.side_effect = Exception("Test error")
    
    # Test data
    payload = {
        'subject': 'Test Subject',
        'content': 'Test Content',
        'timestamp': datetime.now(UTC).isoformat(),
        'recipients': 'test@example.com'
    }
    
    # Call endpoint
    response = client.post('/api/save_emails', 
                          data=json.dumps(payload),
                          content_type='application/json')
    
    # Verify response
    assert response.status_code == 400
    
    # Parse JSON response
    data = json.loads(response.data)
    
    # Verify data
    assert 'message' in data
    assert 'Error occurred' in data['message']
    assert 'Test error' in data['message']
