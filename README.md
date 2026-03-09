# 2026_1_travel

Travel planner web app built with Flask, MariaDB, and server-rendered templates.

## Features

- User signup/login with password hashing
- Session-based authentication
- Create, update, delete travel destinations
- Country picker from predefined list
- Optional start/end dates with date validation
- Optional image upload for destinations (max 5 MB)
- Friendly inline error messages in the UI

## Tech Stack

- Python 3.9
- Flask
- MariaDB
- phpMyAdmin
- HTML/CSS/JS (MixHTML-based interactions)
- Docker + Docker Compose

## Project Structure

- `app.py`: Flask routes and business logic
- `x.py`: Validation, DB helper, no-cache decorator
- `country.py`: Shared country list for destination forms
- `templates/`: Jinja templates
- `static/`: CSS, JS, uploaded images
- `docker-compose.yml`: Local multi-container setup
- `2026_1_travel (1).sql`: Database schema

## Prerequisites

- Docker Desktop (or Docker Engine + Compose)

## Quick Start (Recommended)

1. Start containers:

```bash
docker compose up --build
```

2. Open the app:

- App: `http://localhost/`
- phpMyAdmin: `http://localhost:8080/`

3. Import database schema in phpMyAdmin:

- Server: 
- User: 
- Password: 
- Database: 
- Import file:

4. Use the app:

- Create a user on `/signup`
- Login on `/login`
- Manage destinations on `/destinations`

## Useful Commands

Start in background:

```bash
docker compose up -d --build
```

Stop services:

```bash
docker compose down
```

Stop and remove volumes (resets DB data):

```bash
docker compose down -v
```

## Notes

- The app container runs Flask on port `80`.
- Destination images are stored in `static/uploads`.
- Allowed image types: `png`, `jpg`, `jpeg`, `webp`, `gif`.
- Date validation prevents past dates and end date before start date.

## Default Service Ports

- Web app: `80`
- phpMyAdmin: `8080`
- MariaDB (container mapping): `3307`

## License

No license file is currently included in this repository.
