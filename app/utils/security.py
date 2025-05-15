"""Security utilities for safe HTML handling."""

from __future__ import annotations

import html
from typing import Any

from markupsafe import Markup


def safe_markup(message: str, *args: Any) -> Markup:
    """
    Create safe HTML markup by escaping user input.

    Args:
        message: The message template with placeholders
        *args: Arguments to be safely interpolated

    Returns:
        Safe HTML markup with escaped user input
    """
    # Escape all arguments to prevent XSS
    safe_args = [html.escape(str(arg)) for arg in args]

    # Format the message with escaped arguments
    safe_message = message.format(*safe_args)

    # Return as Markup since content is now safe
    return Markup(safe_message)  # nosec B704


def safe_error_message(error: Exception) -> Markup:
    """
    Create a safe error message for display.

    Args:
        error: The exception to create message for

    Returns:
        Safe HTML markup for error display
    """
    # Escape the error message to prevent XSS
    safe_error = html.escape(str(error))

    # Return structured error message
    return Markup(f"<strong>Error!</strong> {safe_error}")  # nosec B704
