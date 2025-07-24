from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, Length, Email
from datetime import datetime, UTC


class BaseItemsForm(FlaskForm):
    """Base form class for items with common fields."""
    name = StringField('Subject', validators=[DataRequired(),
                                          Length(min=1, max=254)])
    notes = TextAreaField('Email Content', validators=[DataRequired()])
    recipients = StringField('Recipients (comma separated)', 
                          validators=[DataRequired()],
                          description="Enter email addresses separated by commas")
    schedule_time = DateTimeField('Schedule Time', 
                                format='%Y-%m-%dT%H:%M',
                                validators=[DataRequired()],
                                description="When to send the email",
                                default=datetime.now(UTC).replace(second=0, microsecond=0))


class ItemsForm(BaseItemsForm):
    """Form for adding new items."""
    pass


class EditItemsForm(BaseItemsForm):
    """Form for editing existing items."""
    is_done = BooleanField('Email Sent')
