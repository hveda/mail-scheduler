"""Additional tests for job functions."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, UTC

from app.event.jobs import dt_utc, add_recipients, add_event, schedule_mail


def test_dt_utc_with_timezone():
    """Test dt_utc with a timezone-aware datetime string."""
    # Test with an explicit timezone
    dt_str = "2025-05-10 12:00:00+08:00"  # Singapore time
    result = dt_utc(dt_str)
    
    # Should be converted to UTC (8 hours earlier)
    expected = datetime(2025, 5, 10, 4, 0, 0)  # UTC time
    assert result == expected


def test_dt_utc_without_timezone():
    """Test dt_utc with a timezone-naive datetime string."""
    # Local timezone will be applied first, then converted to UTC
    with patch('app.event.jobs.get_localzone') as mock_tz:
        # Mock the local timezone to be UTC+8
        mock_tz.return_value = MagicMock(utcoffset=lambda dt: timedelta(hours=8))
        
        dt_str = "2025-05-10 12:00:00"  # Local time (no TZ info)
        result = dt_utc(dt_str)
        
        # Should be converted to UTC (8 hours earlier)
        expected = datetime(2025, 5, 10, 4, 0, 0)  # UTC time
        assert result == expected


def test_add_recipients(db, session):
    """Test adding recipients to the database."""
    # Test data
    recipients_str = "test1@example.com, test2@example.com, test3@example.com"
    event_id = 1
    
    # Call the function
    result = add_recipients(recipients_str, event_id)
    
    # Check the result
    assert len(result) == 3
    assert "test1@example.com" in result
    assert "test2@example.com" in result
    assert "test3@example.com" in result
    
    # Verify database entries were created
    from app.database.models import Recipient
    recipients = session.query(Recipient).filter_by(event_id=event_id).all()
    assert len(recipients) == 3


@patch('app.event.jobs.schedule_mail')
def test_add_event(mock_schedule, db, session):
    """Test adding an event to the database."""
    # Test data
    data = {
        'subject': 'Test Subject',
        'content': 'Test Content',
        'timestamp': '2025-05-10 12:00:00',
        'recipients': 'test1@example.com, test2@example.com'
    }
    
    # Call the function
    event_id = add_event(data)
    
    # Verify the event was created
    from app.database.models import Event
    event = session.query(Event).get(event_id)
    assert event is not None
    assert event.email_subject == 'Test Subject'
    assert event.email_content == 'Test Content'
    
    # Verify schedule_mail was called
    assert mock_schedule.called
    

@patch('app.event.jobs.rq.get_scheduler')
def test_schedule_mail(mock_get_scheduler, db):
    """Test scheduling a mail job."""
    # Mock the scheduler
    mock_scheduler = MagicMock()
    mock_get_scheduler.return_value = mock_scheduler
    
    # Test data
    event_id = 1
    recipients = ['test@example.com']
    timestamp = datetime.now(UTC) + timedelta(days=1)
    
    # Call the function
    schedule_mail(event_id, recipients, timestamp)
    
    # Verify the job was scheduled
    assert mock_scheduler.enqueue_at.called
    # Check the arguments
    args, kwargs = mock_scheduler.enqueue_at.call_args
    assert args[0] == timestamp  # First arg should be the timestamp
    assert args[1].__name__ == 'send_mail'  # Second arg should be the function
    assert args[2] == event_id  # Third arg should be event_id
    assert args[3] == recipients  # Fourth arg should be recipients
