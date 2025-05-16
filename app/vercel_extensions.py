"""Extensions module for Vercel environment with mocked RQ."""
import os
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate

# Check if we're in Vercel environment
is_vercel = os.environ.get('VERCEL', '0') == '1'

# Initialize extensions
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'

mail = Mail()
migrate = Migrate()

# Create a mock RQ class that doesn't require Redis for Vercel
class MockRQ:
    """Mock implementation of RQ for serverless environments."""
    
    def __init__(self):
        """Initialize the mock RQ instance."""
        self.job = lambda **kwargs: lambda f: f
    
    def init_app(self, app):
        """Initialize the mock RQ with the Flask app."""
        app.config.setdefault('RQ_ASYNC', False)
        return self
    
    def get_scheduler(self, *args, **kwargs):
        """Get a mock scheduler."""
        return MockScheduler()

class MockScheduler:
    """Mock scheduler for serverless environments."""
    
    def enqueue_at(self, timestamp, func, *args, **kwargs):
        """Mock method to enqueue a job at a specific time."""
        return f"mock_job_{func.__name__}"

# Use the mock RQ for Vercel, or real RQ otherwise
if is_vercel:
    rq = MockRQ()
else:
    from flask_rq2 import RQ
    rq = RQ()
