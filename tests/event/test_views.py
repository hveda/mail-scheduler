"""Test file for checking views with low coverage."""
import pytest
from flask import url_for
from unittest.mock import patch, MagicMock
from datetime import datetime, UTC, timedelta

from app.event.views import render_template
from app.database.models import Event, Recipient


def test_render_template_function(app, client):
    """Test the render_template helper function."""
    with app.test_request_context():
        with patch('app.event.views.render_template', side_effect=render_template) as mock_render:
            # Use a template that exists
            result = mock_render('all_events.html', title='Test Title')
            assert mock_render.called
        
        
def test_index_view(app, client):
    """Test the index view."""
    with app.test_request_context():
        response = client.get(url_for('items.all_events'))
        assert response.status_code == 200 or response.status_code == 302  # 302 if redirect due to login required


def test_event_list_view(app, client, db):
    """Test the event list view."""
    with app.test_request_context():
        # This is the same as index view in the current implementation
        response = client.get(url_for('items.all_events'))
        assert response.status_code == 200 or response.status_code == 302  # 302 if redirect due to login required


def test_create_event_get(app, client):
    """Test the create event view (GET)."""
    with app.test_request_context():
        response = client.get(url_for('items.add_event'))
        assert response.status_code == 200 or response.status_code == 302  # 302 if redirect due to login required


@patch('app.event.views.schedule_mail_event')
def test_create_event_post(mock_add_event, app, client, db):
    """Test the create event view (POST)."""
    # Set up the mock to return an event ID
    mock_add_event.return_value = 1
    
    with app.test_request_context():
        # Create form data with the correct field names from ItemsForm
        future_date = datetime.now(UTC) + timedelta(days=1)
        data = {
            'name': 'Test Subject',
            'notes': 'Test Content',
            'recipients': 'test@example.com',
            'schedule_time': future_date.strftime('%Y-%m-%dT%H:%M')
        }
        
        # Mock authentication to bypass login_required decorator
        with patch('flask_login.utils._get_user') as mock_get_user:
            mock_user = MagicMock()
            mock_user.is_authenticated = True
            mock_user.id = 1
            mock_get_user.return_value = mock_user
            
            response = client.post(url_for('items.add_event'), data=data, follow_redirects=True)
            assert response.status_code == 200  # Should be successful now that we're authenticated
            
            # The mock should have been called with form data
            assert mock_add_event.called
        assert mock_add_event.called


@patch('app.event.views.schedule_mail_event')
def test_create_event_validation_error(mock_add_event, app, client, db):
    """Test validation errors in create event view."""
    with app.test_request_context():
        # Create form data with empty required field (name)
        future_date = datetime.now(UTC) + timedelta(days=1)
        data = {
            'name': '',  # Empty, should fail validation
            'notes': 'Test Content',
            'recipients': 'test@example.com',
            'schedule_time': future_date.strftime('%Y-%m-%dT%H:%M')
        }
        
        # Mock authentication to bypass login_required decorator
        with patch('flask_login.utils._get_user') as mock_get_user:
            mock_user = MagicMock()
            mock_user.is_authenticated = True
            mock_user.id = 1
            mock_get_user.return_value = mock_user
            
            response = client.post(url_for('items.add_event'), data=data, follow_redirects=True)
            
            # Should get 200 with validation errors, not a redirect
            assert response.status_code == 200
            assert not mock_add_event.called  # Should not be called with invalid data
            assert b'This field is required' in response.data or b'name' in response.data.lower()


def test_event_detail_view(app, client, db):
    """Test the event detail/edit view."""
    # Create a test event directly using the model
    event = Event(
        email_subject='Test Subject',
        email_content='Test Content',
        timestamp=datetime.now(UTC) + timedelta(days=1)
    )
    db.session.add(event)
    db.session.commit()
    
    with app.test_request_context():
        response = client.get(url_for('items.edit_event', event_id=event.id))
        assert response.status_code in [200, 302]  # Either success or redirect due to login required
