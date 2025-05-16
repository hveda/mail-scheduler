#!/bin/bash
# This script is run during Vercel build step
# It sets up the database and prepares the application

# Set environment flag
export VERCEL=1

# Print dependency versions for debugging
echo "Python version:"
python --version
echo "Pip version:"
pip --version
echo "Dependencies installed:"
pip list

# Check for database URL
if [ -n "$mail_scheduler_DATABASE_URL" ]; then
    echo "PostgreSQL database detected"
    # Install psycopg2 for PostgreSQL support
    pip install psycopg2-binary==2.9.9
    echo "PostgreSQL driver installed"
else
    echo "No PostgreSQL database detected, using SQLite"
fi

# Create the database schema
echo "Setting up database..."
python -c "from api.vercel_app import app, db; with app.app_context(): db.create_all(); print('Database schema created successfully')"

# Print success message
echo "Build completed successfully"
