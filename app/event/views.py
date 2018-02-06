# app/event/views.py

# IMPORTS
from flask import render_template, Blueprint, request, redirect, url_for, flash, Markup
from app.database import db
from app.database.models import Event, Recipient
from .forms import EventsForm, EditEventsForm


# CONFIG
blueprint = Blueprint('items', __name__, template_folder='templates')


# ROUTES
@blueprint.route('/', methods=['GET', 'POST'])
def all_events():
    """Render homepage"""
    all_events = Event.query.all()
    return render_template('all_events.html', items=all_events)


@blueprint.route('/add_event', methods=['GET', 'POST'])
def add_event():
    form = ItemsForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                new_event = Event(form.data)
                db.session.add(new_event)
                db.session.commit()
                message = Markup(
                    "<strong>Well done!</strong> Event added successfully!")
                flash(message, 'success')
                return redirect(url_for('all_events'))
            except:
                db.session.rollback()
                message = Markup(
                    "<strong>Oh snap!</strong>! Unable to add event.")
                flash(message, 'danger')
    return render_template('add_event.html', form=form)


@blueprint.route('/edit_event/<event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    form = EditEventForm(request.form)
    item_with_user = db.session.query(Items, User).join(User).filter(Items.id == items_id).first()
    if item_with_user is not None:
        if current_user.is_authenticated and item_with_user.Items.user_id == current_user.id:
            if request.method == 'POST':
                if form.validate_on_submit():
                    try:
                        item = Items.query.get(items_id)
                        item.name = form.name.data
                        item.notes = form.notes.data
                        db.session.commit()
                        message = Markup("Event edited successfully!")
                        flash(message, 'success')
                        return redirect(url_for('home'))
                    except:
                        db.session.rollback()
                        message = Markup(
                            "<strong>Error!</strong> Unable to edit event.")
                        flash(message, 'danger')
            return render_template('edit_event.html', item=item_with_user, form=form)
        else:
            message = Markup(
                "<strong>Error!</strong> Incorrect permissions to access this item.")
            flash(message, 'danger')
    else:
        message = Markup("<strong>Error!</strong> Item does not exist.")
        flash(message, 'danger')
    return redirect(url_for('home'))

@blueprint.route('/delete_item/<items_id>', methods=['GET', 'POST'])
def delete_item(items_id):
    item_with_user = db.session.query(Items, User).join(User).filter(Items.id == items_id).first()
    if item_with_user is not None:
        items = Items.query.filter_by(id=items_id)
        if current_user.is_authenticated and item_with_user.Items.user_id == current_user.id:
            print(request.method)
            if request.method == 'POST':
                try:
                    db.session.delete(items[0])
                    db.session.commit()
                    message = Markup("<strong>Done.</strong> You have deleted item " + str(items_id) + ".")
                    flash(message, 'success')
                    return redirect(url_for('home'))
                except Exception as e:
                    db.session.rollback()
                    print(e)
                    message = Markup(
                        "<strong>Error!</strong> Unable to delete item.")
                    flash(message, 'danger')
            return render_template('delete_item.html', items=items)
        else:
            message = Markup(
                "<strong>Error!</strong> Incorrect permissions to access this item.")
            flash(message, 'danger')
    else:
        message = Markup("<strong>Error!</strong> Item does not exist.")
        flash(message, 'danger')
    return redirect(url_for('home'))
