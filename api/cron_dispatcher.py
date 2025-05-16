"""
Vercel Cron Job Dispatcher

This script is intended to be run as a Vercel Serverless Function,
triggered by a Vercel Cron Job.

It queries the database for scheduled emails that are due and triggers
the email sending process.
"""
import os
from datetime import datetime, timezone, timedelta

# Need to set up the Flask app context to use SQLAlchemy, config, etc.
# This assumes your create_app and models are accessible.
# Adjust PYTHONPATH in vercel.json if 'app' is not found.
from app import create_app, config as app_config
from app.database.models import Event # Assuming Event model is here
# Assuming send_mail is refactored and directly callable
from app.event.jobs import send_mail, dt_utc # dt_utc might be useful

# Determine which config to use. Vercel sets NODE_ENV, but we use APP_SETTINGS.
# Default to ProductionConfig for Vercel deployments.
active_config_name = os.getenv("APP_SETTINGS", "app.config.ProductionConfig")

# Dynamically get the config class
try:
    if active_config_name.startswith("app."): # e.g., app.config.ProductionConfig
        module_path, class_name = active_config_name.rsplit('.', 1)
        config_module = __import__(module_path, fromlist=[class_name])
        active_config = getattr(config_module, class_name)
    else: # e.g., ProductionConfig (if config.py is directly in PYTHONPATH)
        active_config = getattr(app_config, active_config_name)
except (ImportError, AttributeError) as e:
    print(f"Error loading configuration '{active_config_name}': {e}. Falling back to DevelopmentConfig.")
    active_config = app_config.DevelopmentConfig # Fallback, should not happen in prod

app = create_app(active_config)

def handler(request_event, context): # AWS Lambda-like handler for Vercel
    """
    Vercel Serverless Function Handler for the cron job.
    `request_event` and `context` are passed by Vercel but may not be used here.
    """
    print("Cron dispatcher handler invoked.")
    with app.app_context():
        print(f"Using database URI: {app.config.get(\'SQLALCHEMY_DATABASE_URI\')}")
        now_utc_naive = datetime.now(timezone.utc).replace(tzinfo=None)
        print(f"Current UTC time (naive for DB comparison): {now_utc_naive}")

        try:
            # Query for events that are due and not yet sent.
            # Event.timestamp is stored as naive UTC.
            events_to_send = Event.query.filter(
                Event.timestamp <= now_utc_naive,
                Event.is_done == False
            ).all()

            if not events_to_send:
                print("No emails due to be sent at this time.")
                return {
                    "statusCode": 200,
                    "body": "No emails due to be sent."
                }

            print(f"Found {len(events_to_send)} emails to send.")
            for event in events_to_send:
                print(f"Processing event ID: {event.id}, scheduled for {event.timestamp}")
                # The recipients should be fetched from the event's relationship
                recipients_list = [r.email for r in event.recipients]
                if not recipients_list:
                    print(f"Event ID: {event.id} has no recipients. Marking as done to avoid reprocessing.")
                    event.is_done = True
                    event.done_at = datetime.now(timezone.utc)
                    # db.session.add(event) # Already in session
                    db.session.commit() # Commit change for this event
                    continue

                try:
                    print(f"Attempting to send email for event ID: {event.id} to {recipients_list}")
                    # Ensure send_mail does not have @rq.job decorator anymore
                    # and that it handles its own app context or is called within one.
                    # send_mail itself will set is_done and done_at
                    send_mail(event.id, recipients_list)
                    print(f"Successfully triggered email for event ID: {event.id}")
                except Exception as e:
                    print(f"Error sending email for event {event.id}: {e}")
                    # Optional: Add error handling, e.g., mark event as failed, retry logic
                    # For now, it will be picked up in the next cron run if not marked 'is_done'.

            # db.session.commit() # Commit all changes if send_mail doesn't commit itself
            print("Cron job processing finished.")
            return {
                "statusCode": 200,
                "body": f"Processed {len(events_to_send)} emails."
            }

        except Exception as e:
            print(f"Error in cron dispatcher: {e}")
            # This ensures Vercel knows the cron job encountered an issue.
            return {
                "statusCode": 500,
                "body": f"Error in cron dispatcher: {str(e)}"
            }

# For local testing:
# if __name__ == "__main__":
#     print("Running cron_dispatcher locally...")
#     # Mock Vercel's request and context if needed by your handler
#     mock_event = {}
#     mock_context = {}
#     result = handler(mock_event, mock_context)
#     print(f"Local run result: {result}")
