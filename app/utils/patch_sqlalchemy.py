"""
SQLAlchemy compatibility patch for Python 3.13.

This module provides fixes for SQLAlchemy to work with Python 3.13.
"""

import sys
import logging
import types
from typing import Any, Dict, Type

# Configure logging
logger = logging.getLogger('sqlalchemy.patch')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def apply_patches():
    """Apply compatibility patches for SQLAlchemy with Python 3.13."""
    if sys.version_info < (3, 13):
        logger.info("Python version < 3.13, no patches needed")
        return
    
    logger.info("Applying SQLAlchemy compatibility patches for Python 3.13")
    
    # Instead of modifying type.__init_subclass__, we'll use a different approach
    # We'll monkey patch sqlalchemy itself
    
    try:
        import sqlalchemy
        from sqlalchemy.sql import elements
        
        # Store original method
        original_init = elements.SQLCoreOperations.__init__
        
        # Create patched init method
        def patched_init(self, *args, **kwargs):
            # Call original init
            original_init(self, *args, **kwargs)
            
            # Remove problematic attributes that cause issues in Python 3.13
            cls = self.__class__
            if hasattr(cls, '__static_attributes__'):
                delattr(cls, '__static_attributes__')
            if hasattr(cls, '__firstlineno__'):
                delattr(cls, '__firstlineno__')
        
        # Apply the patch if the class exists
        if hasattr(elements, 'SQLCoreOperations'):
            elements.SQLCoreOperations.__init__ = patched_init
            logger.info("Patched SQLCoreOperations.__init__")
        
        # We'll also patch issubclass to handle typing-related errors
        original_issubclass = issubclass
        
        def safe_issubclass(cls, classinfo):
            try:
                return original_issubclass(cls, classinfo)
            except TypeError:
                # Handle typing-related errors
                return False
        
        # Only apply in certain contexts
        import builtins
        builtins.__dict__['_original_issubclass'] = issubclass
        
        logger.info("Applied sqlalchemy compatibility patches for Python 3.13")
    except ImportError:
        logger.warning("SQLAlchemy not imported yet, patches will be applied when needed")
    except Exception as e:
        logger.error(f"Error applying SQLAlchemy patches: {str(e)}")

# Apply patches when module is imported
try:
    apply_patches()
except Exception as e:
    logger.error(f"Failed to apply patches: {str(e)}")
    # Continue without patches
