from app.database import db
from datetime import datetime


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    email_subject = db.Column(db.String, nullable=False)
    email_content = db.Column(db.String)
    timestamp = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    is_done = db.Column(db.Boolean, nullable=True, default=False)
    done_at = db.Column(db.DateTime, nullable=True)
    recipients = db.relationship('Recipient', backref='event1', lazy='dynamic')

    def __init__(self, email_subject, email_content,
                 timestamp, created_at=None, is_done=None,
                 done_at=None):
        self.email_subject = email_subject
        self.email_content = email_content
        self.timestamp = timestamp
        if created_at is None:
            created_at = datetime.utcnow()
        self.is_done = is_done
        self.done_at = done_at

    def __repr__(self):
        return '<Event ID: {}>'.format(self.id)


class Recipient(db.Model):
    __tablename__ = 'recipients'
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    is_sent = db.Column(db.Boolean, nullable=True, default=False)
    sent_at = db.Column(db.DateTime, nullable=True)

    def __init__(self, email_address, event_id, is_sent=None, sent_at=None):
        self.email_address = email_address
        self.event_id = event_id
        self.is_sent = is_sent
        self.sent_at = sent_at

    def __repr__(self):
        return '<ID: {} Email: {}'.format(self.id, self.email_address)
