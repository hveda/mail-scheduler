"""Tests for API endpoints."""
import json
import pytest
from flask import url_for
from unittest.mock import patch
from datetime import datetime

def test_api_health(client):
    """Test the API health endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'ok'
    assert 'timestamp' in response.json
    
    # Validate timestamp format
    timestamp = response.json['timestamp']
    try:
        datetime.fromisoformat(timestamp)
        is_valid_iso = True
    except ValueError:
        is_valid_iso = False
    assert is_valid_iso, f"Timestamp {timestamp} is not in ISO format"

def test_save_emails_missing_params(client):
    """Test the save_emails endpoint with missing parameters."""
    response = client.post(
        '/api/save_emails',
        data=json.dumps({}),
        content_type='application/json'
    )
    assert response.status_code == 400
    
    # Test with partial data
    partial_payload = {
        'subject': 'Test Email',
        # missing content, timestamp and recipients
    }
    response = client.post(
        '/api/save_emails',
        data=json.dumps(partial_payload),
        content_type='application/json'
    )
    assert response.status_code == 400

def test_save_emails_success(client):
    """Test the save_emails endpoint with valid parameters."""
    payload = {
        'subject': 'Test Email',
        'content': 'This is a test email',
        'timestamp': '07 Feb 2026 12:00 +08',
        'recipients': 'test@example.com'
    }
    response = client.post(
        '/api/save_emails',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 201
    assert 'message' in response.json
    assert 'id' in response.json
    
def test_save_emails_invalid_json(client):
    """Test the save_emails endpoint with invalid JSON."""
    response = client.post(
        '/api/save_emails',
        data="This is not JSON",
        content_type='application/json'
    )
    assert response.status_code == 400
    
def test_save_emails_with_multiple_recipients(client):
    """Test the save_emails endpoint with multiple recipients."""
    payload = {
        'subject': 'Test Multiple Recipients',
        'content': 'This is a test email with multiple recipients',
        'timestamp': '07 Feb 2026 12:00 +08',
        'recipients': 'test1@example.com, test2@example.com, test3@example.com'
    }
    response = client.post(
        '/api/save_emails',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 201
    assert 'message' in response.json
    assert 'id' in response.json
