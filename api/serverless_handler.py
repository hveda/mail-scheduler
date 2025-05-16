"""Serverless function handler for Vercel."""
import os
import sys
from api.index import app


def handler(event, context):
    """Vercel serverless function handler."""
    # Return the ASGI app
    return app
