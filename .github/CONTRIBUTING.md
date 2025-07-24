# Contributing to Mail Scheduler

Thank you for considering contributing to the Mail Scheduler project! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and considerate to other contributors. We aim to foster an inclusive and welcoming community.

## Development Workflow

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes
4. Run the tests locally to ensure everything works
5. Submit a pull request

## Setting Up Development Environment

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

### Using Docker

Alternatively, you can use Docker:

```bash
docker-compose up -d
```

## Running Tests

Before submitting your changes, make sure all tests pass:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app
```

## Code Style

We use flake8 for code style checking. Ensure your code follows our style guidelines:

```bash
flake8 app tests
```

We also recommend using:

- Black for code formatting
- isort for import sorting
- mypy for type checking

## Continuous Integration

We use GitHub Actions for CI/CD. When you submit a pull request, the following checks will run automatically:

### Main CI Pipeline

The main CI pipeline runs on every push to main branch and pull requests. It includes:

- Linting with flake8
- Unit tests with pytest on Python 3.9 and 3.11
- Docker build and test
- Code coverage reporting

### Pull Request Checks

Additional quality checks run on PRs:

- Code style checks (flake8, black, isort)
- Type checking with mypy
- Specific compatibility checks for known issues

### Common CI Issues and Solutions

#### Failing Tests

If tests are failing, check:

1. Console output for specific error messages
2. Whether your changes maintain backward compatibility
3. If you need to update existing tests for new behavior

#### Code Style Issues

If code style checks fail:

1. Run flake8 locally to identify issues
2. Consider using pre-commit hooks to catch issues before committing

#### Markup Import Issues

We've migrated from `flask.Markup` to `markupsafe.Markup`. Make sure you're using the correct import:

```python
# Old (deprecated)
from flask import Markup

# New (correct)
from markupsafe import Markup
```

#### Recipient Constructor Parameters

When using the `Recipient` model, ensure you're using positional arguments not keyword arguments:

```python
# Correct
recipient = Recipient(email, event_id, name, False, None)

# Incorrect
recipient = Recipient(email_address=email, event_id=event_id, name=name, is_sent=False, sent_at=None)
```

## Documentation

If you're adding new features, please update the documentation as well:

1. Update docstrings for new functions and classes
2. Update the API documentation if adding/changing endpoints
3. Add examples if applicable

## Submitting Pull Requests

When submitting a pull request:

1. Reference any related issues in the PR description
2. Provide a clear description of the changes
3. Ensure all checks are passing
4. Request review from maintainers

Thank you for contributing to Mail Scheduler!
