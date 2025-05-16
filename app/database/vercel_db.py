"""Module for initializing database with serverless compatibility."""
import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Check if we're running in Vercel environment
is_vercel = os.environ.get('VERCEL', '0') == '1'

if is_vercel:
    # Configure SQLAlchemy for serverless environment
    engine_options = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
        'connect_args': {'check_same_thread': False}  # For SQLite
    }
    db = SQLAlchemy(engine_options=engine_options)
