"""
RQ-Scheduler compatibility patch.

This module patches the RQ-Scheduler to work with newer versions of RQ
that no longer have the ColorizingStreamHandler class.
"""

import logging
import sys
import importlib.util

# Define the missing class that RQ Scheduler expects
class ColorizingStreamHandler(logging.StreamHandler):
    """
    A replacement for the missing ColorizingStreamHandler class
    that was removed from RQ but is still expected by RQ Scheduler.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_tty = getattr(self.stream, 'isatty', lambda: False)()

def patch_rq_scheduler():
    """
    Patch RQ Scheduler to work with newer versions of RQ.
    This injects the missing ColorizingStreamHandler class into rq.utils module.
    """
    try:
        # Get the rq.utils module
        import rq.utils
        
        # Check if ColorizingStreamHandler is already defined
        if not hasattr(rq.utils, 'ColorizingStreamHandler'):
            # Add the class to the module
            rq.utils.ColorizingStreamHandler = ColorizingStreamHandler
            print("Successfully patched RQ Scheduler compatibility.")
        else:
            print("RQ already has ColorizingStreamHandler, no patch needed.")
    except ImportError as e:
        print(f"Could not patch RQ Scheduler: {str(e)}")

# Apply the patch automatically when this module is imported
patch_rq_scheduler()
