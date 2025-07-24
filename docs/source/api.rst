API Documentation
================

This section documents the REST API endpoints available in the Mail Scheduler application.

Endpoints
---------

Health Check
~~~~~~~~~~~

.. http:get:: /api/health

   Check the health status of the API.

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "status": "ok",
        "timestamp": "2025-05-12T21:27:17.356789Z"
      }

   :statuscode 200: API is healthy

Save Emails
~~~~~~~~~~~

.. http:post:: /api/save_emails

   Schedule a new email to be sent at a specific time.

   **Example request**:

   .. sourcecode:: http

      POST /api/save_emails HTTP/1.1
      Content-Type: application/json

      {
        "subject": "Meeting Reminder",
        "content": "Don't forget our meeting tomorrow at 10am.",
        "timestamp": "13 May 2025 10:00 +08",
        "recipients": "user1@example.com, user2@example.com"
      }

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "message": "Event successfully saved to scheduler",
        "id": 42
      }

   :reqjson string subject: Email subject line
   :reqjson string content: Email body content
   :reqjson string timestamp: Time to send the email (format: "DD MMM YYYY HH:MM TZ")
   :reqjson string recipients: Email recipients, comma separated
   :statuscode 201: Email successfully scheduled
   :statuscode 400: Invalid request data

List Events
~~~~~~~~~~~

.. http:get:: /api/events

   Retrieve a list of all scheduled email events.

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id": 42,
          "email_subject": "Meeting Reminder",
          "email_content": "Don't forget our meeting tomorrow at 10am.",
          "timestamp": "2025-05-13T10:00:00+08:00",
          "created_at": "2025-05-12T21:27:17.356789Z",
          "is_done": false,
          "done_at": null
        },
        {
          "id": 43,
          "email_subject": "Weekly Report",
          "email_content": "Here is the weekly report for May 2025.",
          "timestamp": "2025-05-15T09:00:00+08:00",
          "created_at": "2025-05-12T22:15:30.123456Z",
          "is_done": true,
          "done_at": "2025-05-15T09:00:05.789012Z"
        }
      ]

   :statuscode 200: List of events retrieved successfully
   :statuscode 500: Server error occurred

Get Event Details
~~~~~~~~~~~~~~~~

.. http:get:: /api/events/(int:event_id)

   Retrieve details for a specific scheduled email event.

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 42,
        "email_subject": "Meeting Reminder",
        "email_content": "Don't forget our meeting tomorrow at 10am.",
        "timestamp": "2025-05-13T10:00:00+08:00",
        "created_at": "2025-05-12T21:27:17.356789Z",
        "is_done": false,
        "done_at": null
      }

   :param event_id: The ID of the event to retrieve
   :type event_id: int
   :statuscode 200: Event details retrieved successfully
   :statuscode 404: Event not found
   :statuscode 500: Server error occurred

Swagger Documentation
--------------------

The Mail Scheduler API also provides interactive Swagger documentation at the following URL:

.. code-block:: none

   http://localhost:8080/api/doc

This interface allows you to:

* Explore all available endpoints
* See detailed parameter information
* Test API calls directly from your browser
* View response models and status codes
