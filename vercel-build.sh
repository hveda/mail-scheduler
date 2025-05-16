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

# Create a dummy setup for missing packages
cat > setuptools_mock.py << EOF
import sys
class MockPackage:
    def __getattr__(self, name): return lambda *args, **kwargs: None
sys.modules['pkg_resources'] = MockPackage()
sys.modules['flask_rq2'] = MockPackage()
sys.modules['redis'] = MockPackage()
sys.modules['rq'] = MockPackage()
EOF

# Create the database
echo "Setting up database..."
python -c "import setuptools_mock; from app.vercel_config import VercelConfig; from app.vercel_app import create_app; from app.database import db; app = create_app(VercelConfig); app.app_context().push(); db.create_all()"

# Print success message
echo "Build completed successfully"
