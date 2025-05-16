#!/bin/bash
# Script to deploy simplified Flask app to Vercel

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "Vercel CLI not found. Installing..."
    npm install -g vercel
    echo "Vercel CLI installed."
fi

# Login if needed
echo "Checking Vercel login status..."
vercel whoami &>/dev/null || vercel login

# Prompt for environment variables
read -p "Enter your SECRET_KEY for the application: " SECRET_KEY
read -p "Enter your MAIL_SERVER (default: smtp.example.com): " MAIL_SERVER
MAIL_SERVER=${MAIL_SERVER:-smtp.example.com}
read -p "Enter your MAIL_PORT (default: 587): " MAIL_PORT
MAIL_PORT=${MAIL_PORT:-587}
read -p "Enter your MAIL_USERNAME: " MAIL_USERNAME
read -sp "Enter your MAIL_PASSWORD: " MAIL_PASSWORD
echo ""
read -p "Enter your MAIL_DEFAULT_SENDER (default: mail-scheduler@example.com): " MAIL_DEFAULT_SENDER
MAIL_DEFAULT_SENDER=${MAIL_DEFAULT_SENDER:-mail-scheduler@example.com}
read -p "Use TLS for email? (True/False, default: True): " MAIL_USE_TLS
MAIL_USE_TLS=${MAIL_USE_TLS:-True}

# Generate a random 32 character string if no SECRET_KEY is provided
if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(openssl rand -hex 16)
    echo "Generated random SECRET_KEY: $SECRET_KEY"
fi

# Deploy to Vercel with environment variables
echo "Deploying to Vercel..."
vercel \
  --env SECRET_KEY="$SECRET_KEY" \
  --env MAIL_SERVER="$MAIL_SERVER" \
  --env MAIL_PORT="$MAIL_PORT" \
  --env MAIL_USERNAME="$MAIL_USERNAME" \
  --env MAIL_PASSWORD="$MAIL_PASSWORD" \
  --env MAIL_DEFAULT_SENDER="$MAIL_DEFAULT_SENDER" \
  --env MAIL_USE_TLS="$MAIL_USE_TLS" \
  --env VERCEL="1" \
  --prod

echo "Deployment complete! Your application is now available on Vercel."
