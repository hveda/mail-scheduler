# -*- coding: utf-8 -*-
"""
Flask CLI script.
Set environment variable FLASK_APP=serve.py.
"""
from app import create_app, config

app = create_app(config.DevelopmentConfig)
