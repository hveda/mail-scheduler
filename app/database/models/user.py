"""User model for authentication and authorization."""

from datetime import datetime, UTC
from typing import Optional

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.database import db


class User(db.Model, UserMixin):
    """User model for authentication and authorization."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    _password = db.Column('password_hash', db.String(256), nullable=False)
    first_name = db.Column(db.String(80), nullable=True)
    last_name = db.Column(db.String(80), nullable=True)
    role = db.Column(db.String(20), default='user')  # 'admin', 'user', 'guest'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    last_login = db.Column(db.DateTime, nullable=True)

    @property
    def password(self) -> str:
        """Password property that raises an error when accessed."""
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password: str) -> None:
        """
        Hash and store the user's password.
        
        Args:
            password: The plain text password to hash and store
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        self._password = generate_password_hash(password)

    def verify_password(self, password: str) -> bool:
        """
        Verify a password against the stored hash.
        
        Args:
            password: The plain text password to verify
            
        Returns:
            bool: True if the password matches, False otherwise
        """
        return check_password_hash(self._password, password)

    @property
    def full_name(self) -> str:
        """Get the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return self.username

    def update_last_login(self) -> None:
        """Update the user's last login time to the current time."""
        self.last_login = datetime.now(UTC)
        db.session.commit()

    def is_admin(self) -> bool:
        """Check if the user has admin role."""
        return self.role == 'admin'

    def __repr__(self) -> str:
        """String representation of the User model."""
        return f"<User {self.username}>"
