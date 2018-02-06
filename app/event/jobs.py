"""Jobs redis queue."""
import dateutil.parser
from datetime import datetime

import pytz
from bs4 import BeautifulSoup
from flask_mail import Message
from tzlocal import get_localzone

from app.database import db
from app.extensions import rq, mail
from app.database.models import Event, Recipient


# Helper function.
def add_recipients(data, event_id):
    """Store recipients in database"""
    mail_addr = (data.replace(' ', '')).split(',')
    for m in mail_addr:
        recipient = Recipient(m, event_id, False, None)
        db.session.add(recipient)
        db.session.commit()
    return mail_addr


def dt_utc(dt):
    """Function helper to convert time to UTC before store to database."""
    local_tz = get_localzone()
    dt = dateutil.parser.parse(dt)
    if dt.tzinfo is None:
        """Assume as local timezone, if no timezone info."""
        dt = dt.replace(tzinfo=local_tz)
    utc_now = dt.astimezone(pytz.utc)
    return utc_now


def schedule_mail(event_id, recipients, timestamp):
    """Function helper to schedule send_mail job."""
    scheduler = rq.get_scheduler()
    scheduler.enqueue_at(timestamp, send_mail, event_id, recipients)


# Main job function.
@rq.job
def send_mail(event_id, recipients):
    """
    Sends an send_email asynchronously using flask rq-scheduler
    Args:
        event_id (Event.id) : Event ID
    Returns:
        None
    Todo: still manually passing recipients value to function,
    cause can't load from db yet.
    This function should be just passing event ID.
    """
    event = Event.query.get(event_id)
    msg = Message(subject=event.email_subject)
    for addr_ in recipients:
        msg.add_recipient(addr_)
    with mail.connect() as conn:
        """If email content has HTML code, it will send as HTML.
           If it just text, it will be send as email body.
        """
        if (BeautifulSoup(event.email_content, 'html.parser').find()):
            msg.html = event.email_content
        else:
            msg.body = event.email_content
        conn.send(msg)

    event.is_done = True
    event.done_at = datetime.utcnow()
    done_at = event.done_at
    db.session.add(event)
    db.session.commit()
    return "Success. Done at {}".format(done_at)


def add_event(data):
    """Create event sent mail and store it to database."""
    email_subject = data.get('subject')
    email_content = data.get('content')
    timestamp = dt_utc(data.get('timestamp'))
    recipients = data.get('recipients')
    event = Event(email_subject, email_content,
                  timestamp, datetime.utcnow(), False, None)
    db.session.add(event)
    db.session.commit()
    list_recipients = add_recipients(recipients, event.id)
    schedule_mail(event.id, list_recipients, timestamp)
    return event.id
