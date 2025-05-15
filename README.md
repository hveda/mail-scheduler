# Mail Scheduler

An automated mail sender using Flask-Mail and asynchronous job scheduling with RQ.

## Updates (May 2025)

- Updated to Python 3.13.3 (from 3.6)
- Upgraded all dependencies to latest compatible versions
- Replaced deprecated packages (e.g., flask-restplus → flask-restx)
- Added comprehensive test suite with pytest
- Improved Docker configuration for better production readiness
- Added health endpoint for monitoring at `/api/health`
- Implemented OOP improvements for better code organization and maintainability
- Added comprehensive API documentation with Sphinx
- Created new API endpoints for retrieving scheduled emails
- Added Swagger UI improvements with better response models
- Implemented GitHub Actions for automated testing and CI/CD

## Continuous Integration

This project uses GitHub Actions for continuous integration and deployment:

### CI/CD Workflows

- **Pull Request Checks** (`pr-checks.yml`): Comprehensive validation for PRs
  - Code quality: Black, isort, flake8, mypy
  - Testing: Full test suite with coverage
  - Compatibility: Multi-Python version testing (3.9-3.12)
  - Documentation: Docstring validation and deprecated import checks

- **Security Analysis** (`security-sast.yml`): Python-native security scanning
  - Static analysis with Bandit, Safety, Semgrep, Pylint
  - Automated PR comments with security summaries
  - Weekly scheduled security audits

- **CI/CD Pipeline** (`ci.yml`): Main integration testing
  - Unit and integration testing with PostgreSQL/Redis
  - Docker availability detection and alternative testing
  - Dockerfile validation and container testing when possible
  - Application startup verification

#### Local Testing

Run the local CI simulation script to test your changes:

```bash
./test-ci-local.sh
```

This script checks:
- Python environment and dependencies
- Code quality (flake8, mypy)
- Application startup
- Docker configuration validation
- Unit test execution

- **Documentation Builder**: Automatically builds and publishes documentation
  - Rebuilds when code or documentation changes
  - Makes documentation artifacts available for review

### Status Badges

[![CI/CD Pipeline](https://github.com/hveda/mail-scheduler/actions/workflows/pr-checks.yml/badge.svg)](https://github.com/hveda/mail-scheduler/actions/workflows/pr-checks.yml)
[![Security SAST](https://github.com/hveda/mail-scheduler/actions/workflows/security-sast.yml/badge.svg)](https://github.com/hveda/mail-scheduler/actions/workflows/security-sast.yml)
[![Documentation](https://github.com/hveda/mail-scheduler/actions/workflows/docs.yml/badge.svg)](https://github.com/hveda/mail-scheduler/actions/workflows/docs.yml)

### Security Scanning

The project includes comprehensive automated security analysis with Python-native tools:

#### Static Application Security Testing (SAST)
- **Bandit**: Scans Python code for common security issues and vulnerabilities
- **Safety**: Checks dependencies against known security vulnerability databases
- **Semgrep**: Advanced security pattern analysis with OWASP rules
- **Pylint Security**: Code quality checks with security-focused plugins

#### Security Features
- **Automated scanning** on every push and pull request
- **Weekly security audits** via scheduled workflows
- **Security report artifacts** stored for 30 days
- **PR comments** with security analysis summaries
- **Critical issue detection** with actionable feedback

#### Security Configuration
Security tools are configured via:
- `pyproject.toml` - Bandit, Black, isort, MyPy, Pytest, Coverage settings
- `.bandit` - Additional Bandit security linter configuration
- `.semgrepignore` - Semgrep ignore patterns for irrelevant files

No external API tokens required - all tools run locally within GitHub Actions.

## Setup

### Local Development

For local development, use the provided setup script:

```bash
# Make the script executable (if needed)
chmod +x setup.sh

# Run the setup script
./setup.sh

# Activate the virtual environment
source venv/bin/activate
```

This will:
1. Create a virtual environment
2. Install all dependencies
3. Install the package in development mode
4. Create a `.env` file from `.env.example` if needed

### Configuration
Rename .env.example to .env
And then set your variable there.

### Using Docker

Quickly run the project using [Docker](https://www.docker.com/) and
[Docker Compose](https://docs.docker.com/compose/):

```bash
docker-compose up -d
```

This will start:
- The Flask application
- A worker for processing jobs
- A scheduler for timed jobs
- PostgreSQL database
- Redis for job queuing

Create the database tables:
```bash
docker-compose exec app flask create_db
```

## Documentation

The Mail Scheduler project comes with comprehensive documentation:

### API Documentation

A detailed API documentation is available that covers all endpoints, request/response formats, and status codes. To build and view the documentation:

```bash
# Generate HTML documentation using the provided script
./generate_docs.py

# Or open the documentation directly (optional --open flag)
./generate_docs.py --open
```

The documentation includes:

- All API endpoints with examples
- Request and response formats
- Status codes and error handling
- Architecture overview
- Module documentation

### Swagger UI

Interactive API documentation is also available via Swagger UI at:

```
http://localhost:8080/api/doc
```

This provides a way to test the API directly from your browser.

### Available Endpoints

- `GET /api/health` - Check API health
- `POST /api/save_emails` - Schedule a new email
- `GET /api/events` - List all scheduled emails
- `GET /api/events/<id>` - Get details of a specific scheduled email

### Asynchronous Job Scheduling with RQ

`RQ` is a [simple job queue](http://python-rq.org/) for Python backed by
[Redis](https://redis.io/).

Start a worker:

```bash
flask rq worker
```

Start a scheduler:

```bash
flask rq scheduler
```

Monitor the status of the queue:

```bash
flask rq info --interval 3
```

For help on all available commands:

```bash
flask rq --help
```

## How to Use

Go to http://localhost:8080/api/doc for the API documentation.

Or you can run in your terminal:

```bash
curl -X POST \
  --header 'Content-Type: application/json' \
  --header 'Accept: application/json' \
  -d '{
    "subject": "Email subject",
    "content": "Email body",
    "timestamp": "10 May 2025 12:00 +08",
    "recipients": "user1@example.com, user2@example.com"
  }' \
  'http://localhost:8080/api/save_emails'
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app

# Run a specific test file
pytest tests/api/test_endpoints.py
```

## Development

See the [todo.md](todo.md) file for ongoing development tasks and progress.

## OOP Architecture

The application follows object-oriented programming principles for better maintainability and extensibility:

### SOLID Principles Implementation

The codebase has been refactored to adhere to SOLID principles:

- **Single Responsibility Principle**: Each class has a single responsibility (e.g., EventService handles only event operations)
- **Open/Closed Principle**: Base classes are open for extension but closed for modification
- **Liskov Substitution Principle**: Services can be used interchangeably where their base types are expected
- **Interface Segregation**: Classes expose only the methods that clients need
- **Dependency Inversion**: High-level modules depend on abstractions rather than concrete implementations

### Service Layer

Services encapsulate business logic and database operations, following SOLID principles:

```python
# Example service usage
from app.services.event_service import EventService

# Get all events
events = EventService.get_all()

# Create a new event
result = EventService.create({
    'name': 'Email Subject',
    'notes': 'Email Content'
})
```

Key service components:
- `BaseService`: Abstract base class defining common service interfaces
- `EventService`: Handles event-related operations
- `RecipientService`: Manages recipient data

### Property Decorators

Models use property decorators for better encapsulation and validation:

```python
class Event(db.Model):
    # Database columns with underscore prefix for encapsulation
    _email_subject = db.Column('email_subject', db.String, nullable=False)

    @property
    def email_subject(self) -> str:
        """Get the email subject."""
        return self._email_subject

    @email_subject.setter
    def email_subject(self, value: str) -> None:
        """Set the email subject with validation."""
        if not value:
            raise ValueError("Email subject cannot be empty")
        self._email_subject = value
```

### Class-based Views

Flask routes use class-based views for better organization:

```python
class EventListView(MethodView):
    """Class-based view for listing all events."""

    def get(self):
        """GET method to display all events."""
        events = EventService.get_all()
        return render_template('all_events.html', items=events)

# Route registration
event_list_view = EventListView.as_view('all_events')
blueprint.add_url_rule('/', view_func=event_list_view)
```

### Form Inheritance

Forms use inheritance to reduce code duplication:

```python
class BaseItemsForm(FlaskForm):
    """Base form class with common fields."""
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=254)])
    notes = StringField('Notes')

class ItemsForm(BaseItemsForm):
    """Form for adding new items."""
    pass

class EditItemsForm(BaseItemsForm):
    """Form for editing existing items."""
    pass
```

For more details on the implementation, refer to:
- `app/services/base.py`: Abstract base service class
- `app/services/event_service.py`: Event service implementation
- `app/event/views.py`: Class-based views
- `app/database/models.py`: Property decorators in models
- `app/event/forms.py`: Form inheritance

### Project Structure

The OOP improvements have led to a more organized project structure:

```
app/
├── __init__.py          # Application factory
├── commands.py          # CLI commands
├── config.py            # Configuration classes
├── extensions.py        # Flask extensions
├── api/                 # API endpoints
│   └── routes.py
├── database/            # Database models
│   ├── __init__.py
│   └── models.py        # Models with property decorators
├── event/               # Web UI
│   ├── forms.py         # Form classes with inheritance
│   ├── jobs.py          # Background jobs
│   ├── templates/       # Jinja templates
│   └── views.py         # Class-based views
└── services/            # Service layer
    ├── __init__.py
    ├── base.py          # Abstract base service
    ├── event_service.py # Event service implementation
    └── README.md        # Service layer documentation
```

### Design Patterns

Several design patterns have been implemented:

1. **Repository Pattern**: Service classes abstract database access
2. **Template Method Pattern**: BaseService defines the algorithm structure that subclasses implement
3. **Adapter Pattern**: Legacy methods in services provide backward compatibility
4. **Factory Pattern**: Application factory pattern in app initialization
5. **Decorator Pattern**: Property decorators for model attributes
