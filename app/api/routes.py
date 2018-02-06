"""Endpoints /save_emails."""

from datetime import datetime, timedelta

from pytz import timezone
from flask import request
from flask_restplus import Namespace, Resource, fields

from app.event.jobs import add_event

ns = Namespace('Event', description='Event submission', path='/')

"""
Serializer for swagger documentation.
As example using Singapore Standart Timezone (SST).
List of recipients mail address separated by comma(s).
"""
sst = timezone('Asia/Singapore')
local_now = (datetime.utcnow() + timedelta(minutes=1)).astimezone(sst)
mail_event = ns.model('SubmitEvent', {
    'subject': fields.String(
        required=True,
        description='Mail subject',
        example="Email subject"
    ),
    'content': fields.String(
        required=True,
        description='Mail content',
        example="Email body"
    ),
    'timestamp': fields.DateTime(
        required=True,
        dt_format='iso8601',
        description='Time mail to sent, format dd mm YYYY HH:MM\n\
                  Assume as server timezone when timezone not provided.',
        example=local_now.strftime("%d %b %Y %H:%M %Z")
    ),
    'recipients': fields.String(
        required=True,
        description='Mail recipients separated by comma(s)',
        pattern='\w+@\w+\.\w+(,\s*\w+@\w+\.\w+)*',
        example="retphern@gmail.com, vedafarm.id@gmail.com"
    ),
})


@ns.route('/save_emails')
class EventApi(Resource):
    """Event api endpoints."""

    @ns.expect(mail_event, validate=True)
    @ns.doc(body='SubmitEvent', code=201)
    def post(self):
        """Submit new Event."""
        event_id = add_event(request.json)
        return "Event ID: {}".format(event_id), 201
