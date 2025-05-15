"""
Check if the Markup imports have been correctly updated \
to use markupsafe.
"""
from app.services.event_service import Markup as EventServiceMarkup
from app.services.base import Markup as BaseServiceMarkup

# Import directly from markupsafe for comparison
from markupsafe import Markup as OriginalMarkup

# Verify all imports are the same class
print("Are all Markup imports the same class?")
print(f"EventServiceMarkup is OriginalMarkup: "
      f"{EventServiceMarkup is OriginalMarkup}")
print(f"BaseServiceMarkup is OriginalMarkup: "
      f"{BaseServiceMarkup is OriginalMarkup}")
