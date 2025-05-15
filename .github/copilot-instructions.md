<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Mail-Scheduler Project

## Project Overview
This is a Flask-based application that schedules and sends emails using Redis queue (RQ) for job scheduling and Flask-Mail for email delivery.

## Project Structure
- `app/` - Main application package
  - `api/` - API endpoints using Flask-RESTX
  - `database/` - Database models and configuration
  - `event/` - Event handling, jobs, and email scheduling
  - `commands.py` - Flask CLI commands
  - `config.py` - Application configuration
  - `extensions.py` - Flask extensions

## Tech Stack
- Python 3.13+
- Flask 2.3.2+
- SQLAlchemy 2.0+
- Flask-RESTX for API with Swagger documentation
- Redis and RQ for job scheduling
- PostgreSQL for database
- Docker for containerization

## Coding Style Guidelines
- Use type hints for all function parameters and return values
- Use f-strings for string formatting
- Follow PEP 8 guidelines
- Include docstrings for all modules, classes, and functions
- Use pytest for testing

## Testing
- All new features should include tests
- Maintain test coverage above 80%
- Use mocks for external services like email and database

## Docker
- The application uses Docker Compose for development
- The stack includes PostgreSQL and Redis services
