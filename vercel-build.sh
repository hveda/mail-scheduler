#!/bin/bash
# This script is run during Vercel build step
# It sets up the database and prepares the application

# Print dependency versions for debugging
echo "Python version:"
python --version
echo "Pip version:"
pip --version
echo "Werkzeug version:"
pip show werkzeug | grep Version
echo "Flask version:"
pip show flask | grep Version
echo "Flask-RestX version:"
pip show flask-restx | grep Version

# Create the database
echo "Setting up database..."
python -c "from app import create_app, database; from app.vercel_config import VercelConfig; app = create_app(VercelConfig); app.app_context().push(); database.db.create_all()"

# Print success message
echo "Build completed successfully"
