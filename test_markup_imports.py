"""
Check if the Markup imports have been correctly updated \
to use markupsafe.
"""

# Import directly from markupsafe for comparison
from markupsafe import Markup as OriginalMarkup

from app.services.base import Markup as BaseServiceMarkup
from app.services.event_service import Markup as EventServiceMarkup

# Verify all imports are the same class
print("Are all Markup imports the same class?")
print(
    "EventServiceMarkup is OriginalMarkup: " f"{EventServiceMarkup is OriginalMarkup}"
)
print("BaseServiceMarkup is OriginalMarkup: " f"{BaseServiceMarkup is OriginalMarkup}")
