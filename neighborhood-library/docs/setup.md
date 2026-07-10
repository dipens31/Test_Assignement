# Setup Guide

## Prerequisites

| Tool | Minimum Version |
|---|---|
| Docker | 24+ |
| Docker Compose | v2 (included in Docker Desktop) |
| Git | any |

No local Python or Node.js installation required — everything runs in containers.

---

## Quick Start

```bash
# 1. Clone the repository
git clone <repo-url>
cd neighborhood-library

# 2. Copy environment variables
cp .env.example .env

# 3. Start all services
docker compose up --build

# 4. Open the app
open http://localhost:3000
```

That's it. Docker Compose will:
- Start PostgreSQL and create both `library` and `library_test` databases
- Run Alembic migrations automatically on backend startup
- Install npm dependencies and build the Next.js app

---

## Environment Variables

Copy `.env.example` to `.env` and adjust as needed.

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql://library_user:library_password@db:5432/library` | Main DB |
| `TEST_DATABASE_URL` | `postgresql://library_user:library_password@db:5432/library_test` | Test DB |
| `BACKEND_HOST` | `0.0.0.0` | Uvicorn bind host |
| `BACKEND_PORT` | `8000` | Uvicorn port |
| `FINE_RATE_PER_DAY` | `0.50` | Overdue fine in USD per day |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |
| `NEXT_PUBLIC_API_BASE_URL` | (empty) | Public-facing API URL (leave empty for Docker) |
| `BACKEND_INTERNAL_URL` | `http://backend:8000` | Backend URL for Next.js rewrites |

---

## Running Services Individually

**Start only the database:**
```bash
docker compose up db
```

**Start only the backend (with DB):**
```bash
docker compose up db backend
```

**Start only the frontend:**
```bash
docker compose up frontend
```

---

## Running Tests

### Backend Tests

```bash
# Inside the backend container
docker compose run --rm backend pytest

# With coverage report
docker compose run --rm backend pytest --cov=app --cov-report=term-missing

# Unit tests only
docker compose run --rm backend pytest tests/unit/

# Integration tests only
docker compose run --rm backend pytest tests/integration/
```

Or run locally (requires Python 3.11 and the `library_test` DB):

```bash
cd backend
pip install -r requirements.txt
TEST_DATABASE_URL="postgresql://library_user:library_password@localhost:5432/library_test" pytest
```

### Frontend Tests

```bash
# Inside the frontend container
docker compose run --rm frontend npm test

# With coverage
docker compose run --rm frontend npm run test:ci
```

Or run locally (requires Node.js 20+):

```bash
cd frontend
npm install
npm test
```

---

## Accessing API Documentation

Once running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Database Migrations

Alembic migrations run automatically at backend container startup. To run manually:

```bash
# Apply all pending migrations
docker compose run --rm backend alembic upgrade head

# Check current revision
docker compose run --rm backend alembic current

# Generate a new migration
docker compose run --rm backend alembic revision --autogenerate -m "your_description"

# Rollback one revision
docker compose run --rm backend alembic downgrade -1
```

---

## Stopping and Cleaning Up

```bash
# Stop all services (keep volumes)
docker compose down

# Stop and remove volumes (WARNING: deletes all data)
docker compose down -v
```

---

## Troubleshooting

**Backend fails to start with "relation does not exist"**
→ The database wasn't ready when Alembic ran. The backend service has `depends_on: db` with a healthcheck — if this persists, check PostgreSQL logs: `docker compose logs db`

**Frontend shows "API connection error"**
→ Verify the backend is healthy: `docker compose ps`. Check `BACKEND_INTERNAL_URL` is set to `http://backend:8000`.

**Test database doesn't exist**
→ The `docker/postgres/init.sql` script creates `library_test` when the container first starts. If you started before that script was in place, run: `docker compose down -v && docker compose up --build`

**Port already in use**
→ Change the host port mappings in `docker-compose.yml` (e.g., `"3001:3000"` for the frontend).
