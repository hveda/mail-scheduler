"""Database initialization script.

This script initializes the database with default values.
"""

import click
from flask.cli import with_appcontext
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Any

from app.database import db
from app.database.models.user import User
from app.database.models import Event, Recipient


def create_default_admin() -> User:
    """
    Create a default admin user if none exists.

    Returns:
        User: The created or existing admin user
    """
    admin = User.query.filter_by(username='admin').first()
    if admin:
        click.echo("Admin user already exists.")
        return admin

    admin = User(
        username='admin',
        email='admin@example.com',
        role='admin',
        first_name='Admin',
        last_name='User'
    )
    admin.password = 'adminpassword'  # This will be hashed

    db.session.add(admin)
    db.session.commit()
    click.echo("Default admin user created.")
    return admin


def create_test_user() -> User:
    """
    Create a test user if none exists.

    Returns:
        User: The created or existing test user
    """
    test_user = User.query.filter_by(username='testuser').first()
    if test_user:
        click.echo("Test user already exists.")
        return test_user

    test_user = User(
        username='testuser',
        email='test@example.com',
        role='user',
        first_name='Test',
        last_name='User'
    )
    test_user.password = 'testpassword'  # This will be hashed

    db.session.add(test_user)
    db.session.commit()
    click.echo("Test user created.")
    return test_user


def create_standard_users() -> List[User]:
    """
    Create multiple standard users for testing purposes.

    Returns:
        List[User]: The created users
    """
    standard_users = []
    user_data = [
        {
            "username": "user1",
            "email": "user1@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "password1"
        },
        {
            "username": "user2",
            "email": "user2@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "password": "password2"
        },
        {
            "username": "user3",
            "email": "user3@example.com",
            "first_name": "Robert",
            "last_name": "Johnson",
            "password": "password3"
        }
    ]

    for data in user_data:
        existing_user = User.query.filter_by(username=data["username"]).first()
        if existing_user:
            standard_users.append(existing_user)
            continue

        user = User(
            username=data["username"],
            email=data["email"],
            role='user',
            first_name=data["first_name"],
            last_name=data["last_name"]
        )
        user.password = data["password"]
        db.session.add(user)
        standard_users.append(user)

    db.session.commit()
    click.echo(f"Created {len(standard_users)} standard users.")
    return standard_users


def create_sample_events() -> List[Event]:
    """
    Create sample events if none exist.

    Returns:
        List[Event]: The created sample events
    """
    if Event.query.count() > 0:
        click.echo("Sample events already exist.")
        return Event.query.all()

    # Get users to associate with events
    admin = User.query.filter_by(username='admin').first()
    test_user = User.query.filter_by(username='testuser').first()
    users = User.query.filter(User.username.in_(
        ['user1', 'user2', 'user3'])).all()

    # Combine all users
    all_users = [admin, test_user] + users if users else [admin, test_user]

    now = datetime.now(UTC)
    events = []

    # Event in the past (already sent)
    past_event = Event(
        email_subject="Past Meeting Reminder",
        email_content="This meeting happened yesterday.",
        timestamp=now - timedelta(days=1),
        is_done=True,
        done_at=now - timedelta(days=1)
    )
    # Assign user_id separately to avoid constructor issues
    if admin:
        past_event.user_id = admin.id

    # Event for today
    today_event = Event(
        email_subject="Today's Meeting Reminder",
        email_content="Don't forget our meeting today at 3pm.",
        timestamp=now + timedelta(hours=2),
        is_done=False
    )
    # Assign user_id separately to avoid constructor issues
    if test_user:
        today_event.user_id = test_user.id

    # Event for tomorrow
    tomorrow_event = Event(
        email_subject="Tomorrow's Status Update",
        email_content="Please prepare your status update for tomorrow's meeting.",
        timestamp=now + timedelta(days=1),
        is_done=False
    )
    # Assign user_id separately to avoid constructor issues
    if users:
        tomorrow_event.user_id = users[0].id

    # Event for next week
    next_week_event = Event(
        email_subject="Weekly Planning Session",
        email_content="We will discuss the sprint goals for next week.",
        timestamp=now + timedelta(days=7),
        is_done=False
    )
    # Assign user_id separately to avoid constructor issues
    if len(users) > 1:
        next_week_event.user_id = users[1].id

    events = [past_event, today_event, tomorrow_event, next_week_event]
    db.session.add_all(events)
    db.session.commit()

    # Add recipients for each event
    add_recipients_to_events(events)

    click.echo(f"Created {len(events)} sample events.")
    return events


def add_recipients_to_events(events: List[Event]) -> None:
    """
    Add sample recipients to the given events.

    Args:
        events: List of events to add recipients to
    """
    # Common recipients
    recipient_data = [
        {"email": "team@example.com", "name": "Team"},
        {"email": "manager@example.com", "name": "Manager"},
        {"email": "client@example.com", "name": "Client"},
        {"email": "support@example.com", "name": "Support Team"}
    ]

    # Add recipients to each event
    for event in events:
        # Add 2-3 recipients to each event
        for i in range(min(len(recipient_data), 3)):
            recipient = Recipient(
                email=recipient_data[i]["email"],
                name=recipient_data[i]["name"],
                event_id=event.id
            )
            db.session.add(recipient)

    db.session.commit()
    click.echo(f"Added recipients to events.")


@click.command("init-db")
@with_appcontext
def init_db_command() -> None:
    """
    Initialize the database with default values.

    This creates tables, default users, and sample data.
    """
    # Create tables
    db.create_all()
    click.echo("Database tables created.")

    # Create default users
    create_default_admin()
    create_test_user()
    create_standard_users()

    # Create sample events
    create_sample_events()

    click.echo("Database initialization completed.")


def register_commands(app) -> None:
    """
    Register database commands with the Flask application.

    Args:
        app: The Flask application
    """
    app.cli.add_command(init_db_command)
