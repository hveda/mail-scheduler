Architecture
============

This document describes the architecture of the Mail Scheduler application.

Overview
--------

Mail Scheduler is a Flask-based application that provides both a web interface and a REST API for scheduling emails. The application follows a layered architecture with clear separation of concerns.

Components
----------

The application consists of the following main components:

1. **Web UI**: Flask templates for manual management of scheduled emails
2. **REST API**: RESTful endpoints for integrating with other applications
3. **Service Layer**: Business logic encapsulation
4. **Data Access Layer**: Database models and operations
5. **Job Queue**: Background processing with Redis Queue (RQ)

Layered Architecture
-------------------

.. code-block:: none

   +-------------------+
   |     Web UI / API  |
   +-------------------+
   |    Service Layer  |
   +-------------------+
   |  Data Access Layer|
   +-------------------+
   |      Database     |
   +-------------------+

OOP Implementation
-----------------

The application implements object-oriented programming principles for better maintainability and extensibility:

SOLID Principles
~~~~~~~~~~~~~~~

* **Single Responsibility Principle**: Each class has a single responsibility (e.g., EventService handles only event operations)
* **Open/Closed Principle**: Base classes are open for extension but closed for modification
* **Liskov Substitution Principle**: Services can be used interchangeably where their base types are expected
* **Interface Segregation**: Classes expose only the methods that clients need
* **Dependency Inversion**: High-level modules depend on abstractions rather than concrete implementations

Service Layer
~~~~~~~~~~~~

Services encapsulate business logic and database operations:

.. code-block:: python

   # Example service usage
   from app.services.event_service import EventService

   # Get all events
   events = EventService.get_all()

   # Create a new event
   result = EventService.create({
       'name': 'Email Subject',
       'notes': 'Email Content'
   })

Key service components:

* ``BaseService``: Abstract base class defining common service interfaces
* ``EventService``: Handles event-related operations
* ``RecipientService``: Manages recipient data

Model Properties
~~~~~~~~~~~~~~~

Models use property decorators for better encapsulation and validation:

.. code-block:: python

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

Class-based Views
~~~~~~~~~~~~~~~

Flask routes use class-based views for better organization:

.. code-block:: python

   class EventListView(MethodView):
       """Class-based view for listing all events."""

       def get(self):
           """GET method to display all events."""
           events = EventService.get_all()
           return render_template('all_events.html', items=events)

   # Route registration
   event_list_view = EventListView.as_view('all_events')
   blueprint.add_url_rule('/', view_func=event_list_view)

Project Structure
----------------

.. code-block:: none

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
