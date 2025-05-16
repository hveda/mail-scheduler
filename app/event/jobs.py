"""Jobs for email scheduling and sending."""
import dateutil.parser
from datetime import datetime, UTC
from typing import List, Optional, Dict, Any, Union

import pytz
from bs4 import BeautifulSoup
from flask_mail import Message
from tzlocal import get_localzone

from app.database import db
from app.extensions import mail
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
        name = None
        email = m
        if '<' in m and '>' in m:
            parts = m.split('<')
            if len(parts) == 2 and '>' in parts[1]:
                name = parts[0].strip()
                email = parts[1].split('>')[0].strip()
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
        Datetime object in UTC (naive)
    """
    local_tz = get_localzone()
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=local_tz)
        utc_dt = dt.astimezone(pytz.UTC)
        return utc_dt.replace(tzinfo=None)
    try:
        parsed_dt = dateutil.parser.parse(dt)
        if parsed_dt.tzinfo is None:
            parsed_dt = local_tz.localize(parsed_dt)
        utc_now = parsed_dt.astimezone(pytz.UTC)
        return utc_now.replace(tzinfo=None)
    except Exception as e:
        print(f"Error parsing datetime: {e}")
        return datetime.now(UTC).replace(tzinfo=None)


# Main job function.
def send_mail(event_id: int) -> str:
    """
    Sends an email. Called by the Vercel cron dispatcher.

    Args:
        event_id: Event ID to send email for

    Returns:
        Success or error message.
    """
    event = Event.query.get(event_id)
    if not event:
        return f"Error: Event {event_id} not found."

    if event.is_done:
        return (f"Event {event_id} has already been processed at "
                f"{event.done_at}.")

    recipients_from_db = [r.email for r in event.recipients]

    if not recipients_from_db:
        event.is_done = True  # Mark as done to avoid reprocessing
        event.done_at = datetime.now(UTC)
        db.session.add(event)
        db.session.commit()
        return f"Event {event_id}: No recipients found. Marked as done."

    msg = Message(subject=event.email_subject)
    for addr_ in recipients_from_db:
        msg.add_recipient(addr_)

    with mail.connect() as conn:
        if BeautifulSoup(event.email_content, 'html.parser').find():
            msg.html = event.email_content
        else:
            msg.body = event.email_content
        conn.send(msg)

    event.is_done = True
    event.done_at = datetime.now(UTC)
    done_at = event.done_at
    db.session.add(event)
    db.session.commit()

    return f"Success. Email for event {event_id} sent. Done at {done_at}"


def add_event(data: Dict[str, Any]) -> int:
    """
    Create an email event and store it to database.
    The Vercel cron job will pick up events based on their timestamp.

    Args:
        data: Dictionary containing email data (subject, content,
              timestamp, recipients, user_id)

    Returns:
        Event ID
    """
    email_subject = data.get('subject')
    email_content = data.get('content')
    timestamp_data = data.get('timestamp')
    recipients_data = data.get('recipients')
    user_id = data.get('user_id')

    timestamp = dt_utc(timestamp_data)

    event = Event(email_subject, email_content,
                  timestamp, datetime.now(UTC), False, None, user_id)

    db.session.add(event)
    db.session.commit()  # Commit event first to get event.id

    add_recipients(recipients_data, event.id)  # This also commits

    print(f"Event {event.id} created. Scheduled for {timestamp}. "
          f"Vercel cron will handle sending.")

    return event.id


def schedule_mail_event(data: Dict[str, Any]) -> int:
    """
    Wrapper function for add_event for data from UI form.

    Args:
        data: Dictionary containing email data from the form

    Returns:
        Event ID
    """
    return add_event(data)
