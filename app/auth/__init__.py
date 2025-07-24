"""Authentication package for user management."""

from flask import Blueprint

# Path to templates is relative to the blueprint's location
# Set template_folder to None to use the app's main templates
blueprint = Blueprint('auth', __name__, url_prefix='/auth')

from app.auth import views
