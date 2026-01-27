# Canvas Lite Backend

Backend service for a simplified learning management system (Canvas-style).

## Tech Stack
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker

## Features (WIP)
- Users (students & instructors)
- Courses & enrollments
- Assignments & submissions
- Grading

## Setup
```bash
docker compose up --build
docker compose exec api alembic upgrade head
docker compose exec api python app/db/seed.py