#!/bin/bash
set -e

# Function to check if Redis is ready
wait_for_redis() {
  echo "Waiting for Redis to be ready..."
  until redis-cli -h redis -p 6379 ping > /dev/null 2>&1; do
    echo "Redis is unavailable - sleeping"
    sleep 1
  done
  echo "Redis is up - continuing"
}

# Function to check if Postgres is ready
wait_for_postgres() {
  echo "Waiting for PostgreSQL to be ready..."
  until pg_isready -h postgres -p 5432 -U postgres > /dev/null 2>&1; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
  done
  echo "PostgreSQL is up - continuing"
}

# Wait for Redis and Postgres to be ready
if [ "$1" = "python" ]; then
  wait_for_redis
  wait_for_postgres

  # Activate virtual environment (should already be in PATH but just to be explicit)
  echo "Activating virtual environment..."
  source $VIRTUAL_ENV/bin/activate
fi

# Execute the command
exec "$@"
