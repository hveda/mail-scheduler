import click

from app.database import db


def create_db():
    """Creates the database."""
    db.create_all()


def drop_db():
    """Drops the database."""
    if click.confirm('Are you sure?', abort=True):
        db.drop_all()


def recreate_db():
    """Same as running drop_db() and create_db()."""
    drop_db()
    create_db()
