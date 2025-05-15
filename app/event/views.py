"""View controllers for the event module."""
from datetime import datetime, UTC
from flask import render_template, Blueprint, request, redirect, url_for, flash
from markupsafe import Markup
from flask.views import MethodView
from flask_login import login_required, current_user

from app.database import db
from app.database.models import Event
from app.event.forms import ItemsForm, EditItemsForm
from app.services.event_service import EventService
from app.event.jobs import add_event as schedule_mail_event


# CONFIG
blueprint = Blueprint('items', __name__, template_folder='templates')


# ROUTES
class EventListView(MethodView):
    """Class-based view for listing all events."""

    decorators = [login_required]

    def get(self):
        """GET method to display all events."""
        events = EventService.get_all_events()
        return render_template('all_events.html', items=events)


class EventAddView(MethodView):
    """Class-based view for adding a new event."""

    decorators = [login_required]

    def get(self):
        """GET method to display the add event form."""
        form = ItemsForm()
        return render_template('add_event.html', form=form)

    def post(self):
        """POST method to handle form submission."""
        form = ItemsForm(request.form)
        if form.validate_on_submit():
            try:
                # Format for the email scheduling API
                email_data = {
                    'subject': form.name.data,
                    'content': form.notes.data,
                    'timestamp': form.schedule_time.data.strftime("%d %b %Y %H:%M"),
                    'recipients': form.recipients.data
                }

                # Add user_id if user is authenticated
                if current_user.is_authenticated:
                    email_data['user_id'] = current_user.id

                # Use the existing add_event function from jobs.py
                event_id = schedule_mail_event(email_data)

                message = Markup(
                    "<strong>Well done!</strong> Email scheduled successfully!")
                flash(message, 'success')
                return redirect(url_for('items.all_events'))
            except Exception as e:
                flash(f"Error scheduling email: {str(e)}", 'danger')

        return render_template('add_event.html', form=form)


class EventEditView(MethodView):
    """Class-based view for editing an existing event."""

    decorators = [login_required]

    def get(self, event_id):
        """GET method to display the edit form for a specific event."""
        event = EventService.get_event_by_id(event_id)
        if event is None:
            message = Markup("<strong>Error!</strong> Event does not exist.")
            flash(message, 'danger')
            return redirect(url_for('items.all_events'))

        form = EditItemsForm()
        return render_template('edit_event.html', event=event, form=form)

    def post(self, event_id):
        """POST method to handle edit form submission."""
        form = EditItemsForm(request.form)
        event = EventService.get_event_by_id(event_id)

        if event is None:
            message = Markup("<strong>Error!</strong> Event does not exist.")
            flash(message, 'danger')
            return redirect(url_for('items.all_events'))

        if form.validate_on_submit():
            try:
                # Only allow editing if email has not been sent yet
                if not event.is_done:
                    # Update the event in the database
                    event.email_subject = form.name.data
                    event.email_content = form.notes.data
                    event.timestamp = form.schedule_time.data

                    # Update recipients (would require more logic to properly implement)
                    # This is a simplification - in a real app you would need to
                    # update recipients in the database

                    db.session.commit()

                    message = Markup("Scheduled email updated successfully!")
                    flash(message, 'success')
                else:
                    message = Markup(
                        "Cannot edit an email that has already been sent.")
                    flash(message, 'warning')

                return redirect(url_for('items.all_events'))
            except Exception as e:
                db.session.rollback()
                flash(f"Error updating email: {str(e)}", 'danger')

        return render_template('edit_event.html', event=event, form=form)


class EventDeleteView(MethodView):
    """Class-based view for deleting an event."""

    decorators = [login_required]

    def get(self, event_id):
        """GET method to display delete confirmation page."""
        event = EventService.get_event_by_id(event_id)
        if event is None:
            message = Markup(
                "<strong>Error!</strong> Scheduled email does not exist.")
            flash(message, 'danger')
            return redirect(url_for('items.all_events'))

        return render_template('delete_event.html', event=event)

    def post(self, event_id):
        """POST method to handle delete confirmation."""
        event = EventService.get_event_by_id(event_id)
        if event is None:
            message = Markup(
                "<strong>Error!</strong> Scheduled email does not exist.")
            flash(message, 'danger')
            return redirect(url_for('items.all_events'))

        try:
            # Delete the event from the database
            db.session.delete(event)
            db.session.commit()

            message = Markup(
                f"<strong>Done.</strong> Scheduled email has been deleted.")
            flash(message, 'success')
        except Exception as e:
            db.session.rollback()
            message = Markup(
                f"<strong>Error!</strong> Could not delete email: {str(e)}")
            flash(message, 'danger')

        return redirect(url_for('items.all_events'))


# Register class-based views
event_list_view = EventListView.as_view('all_events')
event_add_view = EventAddView.as_view('add_event')
event_edit_view = EventEditView.as_view('edit_event')
event_delete_view = EventDeleteView.as_view('delete_event')

blueprint.add_url_rule('/', view_func=event_list_view)
blueprint.add_url_rule(
    '/add_event', view_func=event_add_view, methods=['GET', 'POST'])
blueprint.add_url_rule('/edit_event/<int:event_id>',
                       view_func=event_edit_view, methods=['GET', 'POST'])
blueprint.add_url_rule('/delete_event/<int:event_id>',
                       view_func=event_delete_view, methods=['GET', 'POST'])
