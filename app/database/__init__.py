from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def reset_database():
    from project.database.models import Event, Recipient
    db.drop_all()
    db.create_all()
