"""Jobs redis queue."""
import dateutil.parser
from datetime import datetime, UTC
from typing import List, Optional, Dict, Any, Union

import pytz
from bs4 import BeautifulSoup
from flask_mail import Message
from tzlocal import get_localzone

from app.database import db
from app.extensions import rq, mail
from app.database.models import Event, Recipient


# Helper function.
def add_recipients(data: str, event_id: int) -> List[str]:
    """
    Store recipients in database.

    Args:
        data: Comma-separated email addresses
        event_id: ID of the event to associate recipients with

    Returns:
        List of email addresses
    """
    mail_addr = (data.replace(' ', '')).split(',')
    for m in mail_addr:
        # Try to extract name if email is in format "Name <email@example.com>"
        name = None
        email = m

        # If the format matches "Name <email@example.com>"
        if '<' in m and '>' in m:
            parts = m.split('<')
            if len(parts) == 2 and '>' in parts[1]:
                name = parts[0].strip()
                email = parts[1].split('>')[0].strip()

        # Create a new Recipient - using positional arguments
        recipient = Recipient(email, event_id, name, False, None)
        db.session.add(recipient)
        db.session.commit()
    return mail_addr


def dt_utc(dt: Union[str, datetime]) -> datetime:
    """
    Convert time to UTC before storing to database.

    Args:
        dt: Datetime string or object, possibly with timezone info

    Returns:
        Datetime object in UTC
    """
    local_tz = get_localzone()

    # Handle datetime object input
    if isinstance(dt, datetime):
        # If the datetime has no timezone, assume local
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=local_tz)
        # Convert to UTC
        utc_dt = dt.astimezone(pytz.UTC)
        # Return timezone-naive datetime in UTC
        return utc_dt.replace(tzinfo=None)

    # Handle string input
    try:
        parsed_dt = dateutil.parser.parse(dt)

        # Assume local timezone if no timezone info
        if parsed_dt.tzinfo is None:
            parsed_dt = local_tz.localize(parsed_dt)

        utc_now = parsed_dt.astimezone(pytz.UTC)
        # Return timezone-naive datetime in UTC
        return utc_now.replace(tzinfo=None)
    except Exception as e:
        # If parsing fails, return the current time as a fallback
        print(f"Error parsing datetime: {e}")
        return datetime.now(UTC).replace(tzinfo=None)


def schedule_mail(event_id: int, recipients: List[str], timestamp: datetime) -> None:
    """
    Schedule send_mail job.

    Args:
        event_id: Event ID to send email for
        recipients: List of recipient email addresses
        timestamp: When to send the email
    """
    scheduler = rq.get_scheduler()
    scheduler.enqueue_at(timestamp, send_mail, event_id, recipients)


# Main job function.
@rq.job
def send_mail(event_id: int, recipients: List[str]) -> str:
    """
    Sends an email asynchronously using flask rq-scheduler.

    Args:
        event_id: Event ID to send email for
        recipients: List of recipient email addresses

    Returns:
        Success message with timestamp

    Todo: 
        Use recipients from database rather than passing to function.
        This function should just need the event ID.
    """
    event = Event.query.get(event_id)
    msg = Message(subject=event.email_subject)

    for addr_ in recipients:
        msg.add_recipient(addr_)

    with mail.connect() as conn:
        # If email content has HTML code, send as HTML.
        # If it's just text, send as email body.
        if BeautifulSoup(event.email_content, 'html.parser').find():
            msg.html = event.email_content
        else:
            msg.body = event.email_content

        conn.send(msg)

    # Update event status
    event.is_done = True
    event.done_at = datetime.now(UTC)
    done_at = event.done_at

    db.session.add(event)
    db.session.commit()

    return f"Success. Done at {done_at}"


def add_event(data: Dict[str, Any]) -> int:
    """
    Create an email event and store it to database.

    Args:
        data: Dictionary containing email data (subject, content, timestamp, recipients)

    Returns:
        Event ID
    """
    email_subject = data.get('subject')
    email_content = data.get('content')
    timestamp_data = data.get('timestamp')
    recipients = data.get('recipients')
    user_id = data.get('user_id')

    # Convert timestamp to UTC datetime, handling both string and datetime inputs
    timestamp = dt_utc(timestamp_data)

    event = Event(email_subject, email_content,
                  timestamp, datetime.now(UTC), False, None, user_id)

    db.session.add(event)
    db.session.commit()

    list_recipients = add_recipients(recipients, event.id)
    schedule_mail(event.id, list_recipients, timestamp)

    return event.id


def schedule_mail_event(data: Dict[str, Any]) -> int:
    """
    Wrapper function for add_event that handles data coming from the UI form.

    Args:
        data: Dictionary containing email data from the form
            (subject, content, timestamp, recipients)

    Returns:
        Event ID
    """
    # Use the existing add_event function to maintain consistency
    return add_event(data)
