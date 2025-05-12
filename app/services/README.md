# filepath: /Users/herirusmanto/Learn/Sibermu/mail-scheduler/app/services/README.md
# Services Module

This module implements service classes that follow the SOLID principles and provide a consistent interface for business logic operations.

## Architecture

The services module is designed with the following principles:

1. **Single Responsibility Principle**: Each service class handles operations related to a single domain entity
2. **Open/Closed Principle**: The `BaseService` abstract class allows for extension without modification
3. **Liskov Substitution Principle**: All service implementations can be used interchangeably where the base class is expected
4. **Interface Segregation**: Services expose only methods that clients need
5. **Dependency Inversion**: High-level modules (routes) depend on abstractions (service interfaces), not concrete implementations

## Classes

### BaseService

An abstract base class that defines the common interface for all service classes:

- `get_all()`: Retrieves all items of a specific type
- `get_by_id(item_id)`: Retrieves a single item by ID
- `create(data)`: Creates a new item
- `update(item_id, data)`: Updates an existing item
- `delete(item_id)`: Deletes an item

### EventService

Service for event-related operations:

- Implements all methods from `BaseService`
- Provides legacy adapter methods for backward compatibility
- Handles event creation, retrieval, updating, and deletion

### RecipientService

Service for recipient-related operations:

- Implements all methods from `BaseService`
- Provides additional methods specific to recipients, such as `get_by_event_id`
- Handles bulk operations like `bulk_create`

## Usage

Services should be used from controllers/views to perform business operations. They encapsulate database access and business logic, providing a clean API for the presentation layer.

Example:

```python
from app.services.event_service import EventService

# Get all events
events = EventService.get_all()

# Get a specific event
event = EventService.get_by_id(event_id)

# Create a new event
result = EventService.create({
    'name': 'Event Name',
    'notes': 'Event Notes',
    # other fields...
})

# Update an event
success = EventService.update(event_id, {
    'name': 'Updated Name',
    'notes': 'Updated Notes',
})

# Delete an event
success = EventService.delete(event_id)
```
