"""Jobs redis queue."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict, List, Union, cast

import dateutil.parser
import pytz
from bs4 import BeautifulSoup
from flask_mail import Message
from tzlocal import get_localzone

from app.database import db
from app.database.models import Event, Recipient
from app.extensions import mail, rq


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
    mail_addr = (data.replace(" ", "")).split(",")
    for m in mail_addr:
        # Try to extract name if email is in format "Name <email@example.com>"
        name = None
        email = m

        # If the format matches "Name <email@example.com>"
        if "<" in m and ">" in m:
            parts = m.split("<")
            if len(parts) == 2 and ">" in parts[1]:
                name = parts[0].strip()
                email = parts[1].split(">")[0].strip()

        # Create a new Recipient - using correct constructor signature
        recipient = Recipient(email=email, name=name, event_id=event_id)
        db.session.add(recipient)

    # Commit all recipients at once
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
    # Handle datetime object input
    if isinstance(dt, datetime):
        # If the datetime has no timezone, assume local
        if dt.tzinfo is None:
            # Get local timezone and handle both pytz and ZoneInfo types
            local_tz = get_localzone()
            if hasattr(local_tz, "localize"):
                # pytz timezone
                local_dt = local_tz.localize(dt)
            else:
                # ZoneInfo timezone
                local_dt = dt.replace(tzinfo=local_tz)
        else:
            local_dt = dt
        # Convert to UTC
        utc_dt: datetime = local_dt.astimezone(pytz.UTC)
        # Return timezone-naive datetime in UTC
        return utc_dt.replace(tzinfo=None)

    # Handle string input
    try:
        # Special handling for timezone abbreviations like "US/Pacific"
        if " US/Pacific" in dt:
            dt_str = dt.replace(" US/Pacific", "")
            parsed_dt = dateutil.parser.parse(dt_str)
            pacific_tz = pytz.timezone("US/Pacific")
            parsed_dt = pacific_tz.localize(parsed_dt)
        else:
            parsed_dt = dateutil.parser.parse(dt)

        # Assume local timezone if no timezone info
        if parsed_dt.tzinfo is None:
            # Get local timezone and handle both pytz and ZoneInfo types
            local_tz = get_localzone()
            if hasattr(local_tz, "localize"):
                # pytz timezone
                parsed_dt = local_tz.localize(parsed_dt)
            else:
                # ZoneInfo timezone
                parsed_dt = parsed_dt.replace(tzinfo=local_tz)

        utc_dt = parsed_dt.astimezone(pytz.UTC)
        # Return timezone-naive datetime in UTC
        return utc_dt.replace(tzinfo=None)
    except Exception as e:
        # For truly invalid formats that can't be parsed at all, raise
        if "not a valid timestamp" in str(dt) or "unknown" in str(e).lower():
            raise Exception(f"Invalid datetime format: {dt}")
        # If parsing fails, return the current time as a fallback
        print(f"Error parsing datetime: {e}")
        utc_now = datetime.now(UTC)
        return utc_now.replace(tzinfo=None)


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
    event = db.session.get(Event, event_id)
    if not event:
        raise ValueError(f"Event with ID {event_id} not found")

    msg = Message(subject=event.email_subject)

    for addr_ in recipients:
        msg.add_recipient(addr_)

    with mail.connect() as conn:
        # If email content has HTML code, send as HTML.
        # If it's just text, send as email body.
        if BeautifulSoup(event.email_content, "html.parser").find():
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
        data: Dictionary containing email data (subject, content, timestamp,
              recipients)

    Returns:
        Event ID
    """
    email_subject = data.get("subject")
    email_content = data.get("content")
    timestamp_data = data.get("timestamp")
    recipients = data.get("recipients")
    # user_id = data.get("user_id")  # Currently unused

    # Validate required parameters
    if not email_subject:
        raise ValueError("Email subject is required")
    if not email_content:
        raise ValueError("Email content is required")
    if not timestamp_data:
        raise ValueError("Timestamp is required")
    if not recipients:
        raise ValueError("Recipients are required")

    # Convert timestamp to UTC datetime, handling both string and datetime
    # inputs
    timestamp = dt_utc(timestamp_data)

    event = Event(
        email_subject=email_subject,
        email_content=email_content,
        timestamp=timestamp,
        created_at=datetime.now(UTC),
        is_done=False,
        done_at=None,
    )

    db.session.add(event)
    db.session.commit()

    list_recipients = add_recipients(recipients, event.id)
    schedule_mail(event.id, list_recipients, timestamp)

    return cast(int, event.id)


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
