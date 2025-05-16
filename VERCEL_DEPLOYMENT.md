# Mail Scheduler - Vercel Deployment Guide

This guide provides instructions for deploying the Mail Scheduler application to Vercel.

## Prerequisites

1. A [Vercel account](https://vercel.com/signup)
2. [Vercel CLI](https://vercel.com/docs/cli) installed (optional for CLI deployment)
3. Git repository with your Mail Scheduler code

## Deployment Steps

### Option 1: Deploy with Vercel CLI

1. Install Vercel CLI
   ```bash
   npm install -g vercel
   ```

2. Login to Vercel
   ```bash
   vercel login
   ```

3. Deploy from your project directory
   ```bash
   cd mail-scheduler
   vercel
   ```

4. Follow the prompts to complete the deployment.

### Option 2: Deploy via Vercel Dashboard

1. Push your code to a Git provider (GitHub, GitLab, or Bitbucket)
2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click "New Project"
4. Import your Git repository
5. Configure the project:
   - Framework Preset: Other
   - Root Directory: ./
   - Build Command: None
   - Output Directory: None
   - Install Command: pip install -r requirements-vercel.txt
6. Click "Deploy"

## Environment Variables

Set the following environment variables in your Vercel project settings:

- `SECRET_KEY` - A secure random string
- `MAIL_SERVER` - SMTP server address
- `MAIL_PORT` - SMTP server port
- `MAIL_USERNAME` - SMTP username
- `MAIL_PASSWORD` - SMTP password
- `MAIL_DEFAULT_SENDER` - Default sender email
- `MAIL_USE_TLS` - Set to "True" to use TLS

## Limitations

When deployed on Vercel:

1. The application uses SQLite database which may be reset periodically due to Vercel's serverless architecture.
2. Redis Queue functionality is disabled.
3. Long-running processes are not supported.

For production deployments requiring a persistent database and background task processing, consider using a traditional hosting service instead.

## Troubleshooting

- Check Vercel logs in the Vercel Dashboard under the Functions tab
- Ensure all required environment variables are set
- Verify that your requirements-vercel.txt contains all necessary dependencies
