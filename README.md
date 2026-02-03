# Turing Taste - Cloud Restaurant Ordering System

A cloud-based restaurant ordering application built on Google Cloud Platform.

## Tech Stack
- **Backend**: Flask (Python)
- **Databases**: Cloud SQL (PostgreSQL), Cloud Datastore (NoSQL)
- **Authentication**: Google OAuth 2.0
- **Hosting**: Google App Engine
- **Frontend**: Bootstrap 5

## Features
- User authentication via Google OAuth
- Browse restaurant menu from Cloud SQL database
- Place orders stored in Cloud Datastore
- View order history
- REST API endpoints

## Architecture
- Cloud SQL stores structured menu items
- Datastore stores flexible order documents
- OAuth delegates authentication to Google
- App Engine provides managed hosting

## Setup
1. Configure Google Cloud project
2. Set environment variables in `.env`
3. Deploy: `gcloud app deploy`

## Security
- Environment variables for sensitive credentials
- OAuth 2.0 for authentication
- Parameterized SQL queries
- Server-side session management

## Testing
Run unit tests: `python3 test_app.py`
