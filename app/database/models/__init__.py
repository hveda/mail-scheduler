"""Database models package."""
# Import user model
from app.database.models.user import User

# Import core models
from app.database.models_core import Event, Recipient

# Define legacy compatibility for EventRecipient
EventRecipient = Recipient

# Define __all__ to control what's imported with `from app.database.models import *`
__all__ = ['User', 'Event', 'Recipient', 'EventRecipient']
