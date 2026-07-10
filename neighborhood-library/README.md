# Neighborhood Library Service

A fullstack library management system for books, members, and lending operations with a modern, production-grade UI.

## What Was Built

This is a complete library management application featuring:

- **Backend API** (Python 3.11 + FastAPI + PostgreSQL)
  - RESTful API for books, members, and loans
  - Automatic overdue fine calculation ($0.50/day)
  - Database migrations via Alembic
  - Comprehensive test suite (88 tests - unit + integration)
  - Demo data seeding (10 books, 5 members, 6 loans)
  - Structured logging with file persistence
  - Duplicate loan prevention with row locking
  - Schema validation with input trimming

- **Frontend UI** (Next.js 14 + React + TypeScript + Tailwind CSS)
  - Modern, polished design with indigo/violet brand palette
  - Pages: Dashboard, Books, Members, Loans, Overdue Loans, Borrow, Return
  - Copyable IDs in tables (Book ID, Member ID, Loan ID)
  - Toast notifications for user feedback
  - Skeleton loading states
  - Form validation with react-hook-form
  - Responsive design

- **Infrastructure**
  - Docker Compose orchestration
  - PostgreSQL database with automatic test DB setup
  - API proxy via Next.js rewrites

---

## Quick Start (Docker)

### Prerequisites
- Docker and Docker Compose installed
- No other services using ports 3000, 5432, or 8000

### Baby-Step Setup

**Step 1: Clone and configure**
```bash
# Navigate to project directory
cd neighborhood-library

# Copy environment file (optional - defaults work for Docker)
cp .env.example .env
```

**Step 2: Build and start services**
```bash
# Build images and start all services (this may take 5-10 minutes first time)
docker compose up --build
```

**Step 3: Run database migrations**
```bash
# In a new terminal, run migrations to create tables
docker compose exec backend alembic upgrade head
```

**Step 4: Seed demo data**
```bash
# Populate database with sample data (8 books, 5 members, 6 loans)
docker compose exec backend python seed.py
```

**Step 5: Verify everything is running**
```bash
# Check all services are healthy
docker compose ps

# Test backend health
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000
```

### Access Points

- **Frontend UI:** http://localhost:3000
- **Backend API:** http://localhost:8000/api/v1
- **API Docs (Swagger):** http://localhost:8000/docs
- **API Docs (ReDoc):** http://localhost:8000/redoc
- **Database:** localhost:5432 (user: `library_user`, password: `library_password`, db: `library`)

---

## Stopping and Cleaning

```bash
# Stop services (keeps data)
docker compose stop

# Stop and remove containers (keeps data)
docker compose down

# Stop and remove everything including volumes (deletes all data)
docker compose down --volumes
```

---

## Project Structure

```
.
├── backend/                   # Python FastAPI service
│   ├── app/
│   │   ├── api/v1/            # Route handlers (books, members, loans)
│   │   ├── core/              # Config, DB session, custom exceptions
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── repositories/      # Data-access layer
│   │   ├── schemas/           # Pydantic request/response models
│   │   └── services/          # Business logic (borrow/return/fines)
│   ├── alembic/               # DB migrations
│   ├── seed.py                # Demo data seeding script
│   └── tests/                 # Unit + integration tests
├── frontend/                  # Next.js 14 (App Router) service
│   ├── app/                   # Pages and layouts
│   ├── components/            # Reusable UI components
│   │   ├── books/             # BookForm
│   │   ├── members/           # MemberForm
│   │   ├── loans/             # BorrowForm, ReturnForm
│   │   ├── layout/            # Navbar
│   │   └── ui/                # Toast, Modal, Alert, Skeleton, Spinner, DataTable, ErrorBoundary
│   ├── lib/
│   │   ├── api/               # Typed API client wrappers
│   │   └── constants.ts      # Centralized API endpoint constants
│   └── __tests__/             # Jest + React Testing Library tests
├── docker/
│   └── postgres/
│       └── init.sql           # Test database initialization
├── docs/                      # Architecture, schema, API, setup docs
├── docker-compose.yml
├── .env.example
└── .gitignore
```

---

## Running Tests

### Backend Tests

The backend has both unit and integration tests covering:
- Business logic (fine calculation, loan operations)
- API endpoints (CRUD operations for books, members, loans)
- Database operations

```bash
# Run all backend tests inside Docker
docker compose exec backend pytest tests/ -v --cov=app --cov-report=term-missing

# Run only unit tests
docker compose exec backend pytest tests/unit/ -v

# Run only integration tests
docker compose exec backend pytest tests/integration/ -v

# Run with coverage report
docker compose exec backend pytest tests/ -v --cov=app --cov-report=html
```

### Frontend Tests

The frontend has component tests using Jest and React Testing Library:
- Form validation (BookForm, MemberForm, BorrowForm, ReturnForm)
- API client error handling

```bash
# Run all frontend tests inside Docker
docker compose exec frontend npm test

# Run tests in watch mode
docker compose exec frontend npm test -- --watch

# Run tests with coverage
docker compose exec frontend npm test -- --coverage
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | *(required)* | PostgreSQL connection string |
| `TEST_DATABASE_URL` | *(required for tests)* | Separate test DB |
| `BACKEND_HOST` | `0.0.0.0` | Uvicorn bind host |
| `BACKEND_PORT` | `8000` | Uvicorn port |
| `FINE_RATE_PER_DAY` | `0.50` | USD fine per overdue day |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed CORS origins |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Frontend → backend URL |
| `BACKEND_INTERNAL_URL` | `http://backend:8000` | Docker network URL |

See `.env.example` for all variables.

---

## Demo Data

The seed script creates:
- **10 Books:** Various programming books (Clean Code, The Pragmatic Programmer, etc.)
- **5 Members:** Sample library members
- **6 Loans:** Mixed statuses (2 BORROWED, 2 RETURNED, 2 OVERDUE with fines)

To reseed data:
```bash
docker compose exec backend python seed.py
```

---

## Documentation

- [`docs/architecture.md`](docs/architecture.md) — System design and component diagram
- [`docs/schema.md`](docs/schema.md) — Database schema and ERD
- [`docs/api.md`](docs/api.md) — REST API endpoint reference
- [`docs/setup.md`](docs/setup.md) — Detailed setup and local dev guide
- [`docs/adr/`](docs/adr/) — Architecture decision records
