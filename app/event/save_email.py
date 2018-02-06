"""Endpoints /save_emails module."""
import dateutil.parser

import pytz
from tzlocal import get_localzone

from app.database import db
from app.extensions import rq
from app.database.models import Event, Recipient
from app.event.jobs import send_mail


def schedule_mail(event_id, recipients, timestamp):
    """Create schedule job to send mail."""
    scheduler = rq.get_scheduler()
    scheduler.enqueue_at(timestamp, send_mail, event_id, recipients)


def dt_utc(dt):
    """Convert time to UTC before store to database."""
    local_tz = get_localzone()
    dt = dateutil.parser.parse(dt)
    if dt.tzinfo is None:
        """Assume as local timezone, if no timezone info."""
        dt = dt.replace(tzinfo=local_tz)
    utc_now = dt.astimezone(pytz.utc)
    return utc_now


def add_recipients(data, event_id):
    """Store recipients in database"""
    mail_addr = (data.replace(' ', '')).split(',')
    for m in mail_addr:
        recipient = Recipient(m, event_id)
        db.session.add(recipient)
        db.session.commit()
    return mail_addr


def add_event(data):
    """Create event to sent mail"""
    email_subject = data.get('subject')
    email_content = data.get('content')
    timestamp = dt_utc(data.get('timestamp'))
    recipients = data.get('recipients')
    event = Event(email_subject, email_content, timestamp)
    db.session.add(event)
    db.session.commit()
    list_recipients = add_recipients(recipients, event.id)
    schedule_mail(event.id, list_recipients, timestamp)
    return event.id
