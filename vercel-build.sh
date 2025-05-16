#!/bin/bash
# This script is run during Vercel build step
# It sets up the database and prepares the application

# Create the database
python -c "from app import create_app, database; from app.vercel_config import VercelConfig; app = create_app(VercelConfig); app.app_context().push(); database.db.create_all()"

# Print success message
echo "Build completed successfully"
