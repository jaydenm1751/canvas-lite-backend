# Canvas Lite Backend

Backend service for a simplified learning management system (Canvas-style).

A role-based learning management system backend built with FastAPI, PostgreSQL, SQLAlchemy, and Alembic, supporting courses, enrollments, assignments, submissions, grading, and gradebook analytics.

## Tech Stack
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0
- Alembic migrations
- Docker + Docker Compose
- JWT authentication
- Role-based authorization

## System Architecture

- Stateless REST API built with FastAPI
- PostgreSQL relational database with normalized schema
- SQLAlchemy 2.0 ORM for data access and business logic enforcement
- Alembic for versioned database migrations
- JWT-based authentication (Bearer tokens)
- Role-based access control (student vs instructor)
- Dockerized service with reproducible local environment
- Gradebook queries optimized using PostgreSQL features (DISTINCT ON)

## Core Features

- Role-based authentication (student & instructor)
- Course creation and enrollment with duplicate prevention
- Assignment management with due dates and late submission controls
- Multi-attempt submission system
- Idempotent grade upsert (PUT semantics)
- Instructor gradebook view (latest submission per student)
- Permission enforcement at every resource boundary

## Design Decisions

- Grades are restricted to the latest submission per student to prevent grading outdated attempts.
- Database-level constraints enforce unique enrollments and one-grade-per-submission.
- Instructor and student access paths are separated at the endpoint layer to prevent privilege escalation.
- PUT is used for grading to allow idempotent re-grading behavior.

## Setup
```bash
docker compose up --build
docker compose exec api alembic upgrade head
docker compose exec api python app/db/seed.py
```
user and passwords are stored in seed.py for logins.