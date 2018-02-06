from flask import Blueprint
from flask_restplus import Api
from app.api.routes import ns


blueprint = Blueprint('api', __name__)
api = Api(blueprint,
          version='0.1', title='Mail Scheduler',
          description='Automated Mail Sender Scheduler',
          doc='/doc')
api.add_namespace(ns)
