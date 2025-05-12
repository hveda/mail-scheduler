from flask import Blueprint, redirect
from flask_restx import Api
from app.api.routes import ns


blueprint = Blueprint('api', __name__)

@blueprint.route('/')
def index():
    """Redirect API root to documentation."""
    return redirect('/api/doc')

api = Api(blueprint,
          version='0.1', title='Mail Scheduler',
          description='Automated Mail Sender Scheduler<br><a href="/auth/login">Go to Login Page</a>',
          doc='/doc')
api.add_namespace(ns)
