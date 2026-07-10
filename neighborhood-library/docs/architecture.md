# Architecture Overview

## High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│                      docker-compose                      │
│                                                          │
│  ┌────────────────┐   ┌──────────────┐   ┌───────────┐  │
│  │  Next.js       │   │  FastAPI     │   │ PostgreSQL │  │
│  │  Frontend      │──▶│  Backend     │──▶│ Database  │  │
│  │  :3000         │   │  :8000       │   │  :5432    │  │
│  └────────────────┘   └──────────────┘   └───────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Backend

### Stack

| Layer | Technology |
|---|---|
| HTTP Framework | FastAPI |
| ORM | SQLAlchemy 2.x (mapped_column style) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Database | PostgreSQL 15 |
| Runtime | Python 3.11, Uvicorn |

### Module Structure

```
backend/app/
├── core/
│   ├── config.py       # Pydantic Settings (env vars)
│   ├── database.py     # Engine, Session, get_db()
│   ├── exceptions.py   # HTTP exception subclasses
│   ├── logging.py      # Structured logging setup
│   └── validators.py   # Common validation utilities
├── models/
│   ├── base.py         # TimestampMixin
│   ├── book.py         # Book ORM model
│   ├── member.py       # Member ORM model
│   └── loan.py         # Loan ORM model + LoanStatus enum
├── schemas/
│   ├── common.py       # PaginatedResponse, ErrorResponse
│   ├── book.py         # BookCreate/Update/Response (with trimming validation)
│   ├── member.py       # MemberCreate/Update/Response (with trimming validation)
│   └── loan.py         # BorrowRequest, ReturnRequest, LoanResponse
├── repositories/
│   ├── book_repository.py
│   ├── member_repository.py
│   └── loan_repository.py
├── services/
│   ├── book_service.py
│   ├── member_service.py
│   └── loan_service.py   # Fine calculation, borrow/return logic, duplicate prevention
├── api/v1/
│   ├── books.py
│   ├── members.py
│   ├── loans.py
│   └── members_loans.py
└── main.py             # App factory, CORS, router registration
```

### Design Principles

- **Repository pattern**: All database queries live in `repositories/`. Services never call SQLAlchemy directly.
- **Service layer**: All business logic lives in `services/`. Routers delegate to services and never implement business rules.
- **Dependency injection**: `get_db()` is injected into every request via FastAPI `Depends()`. Service objects receive the session at construction time.
- **Row locking**: `SELECT ... FOR UPDATE` on Book rows during borrow to prevent race conditions on `copies_available`.
- **Duplicate prevention**: Active loan checks prevent members from borrowing the same book twice.
- **Fine calculation**: Pure function `calculate_fine(due_at, returned_at, rate)` with half-up rounding for exactness.
- **Logging**: Structured logging with file and console handlers for debugging and monitoring.
- **Validation**: Centralized validators in `core/validators.py` with schema-level trimming and whitespace-only blocking.

## Frontend

### Stack

| Layer | Technology |
|---|---|
| Framework | Next.js 14 (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS + custom `@layer components` utilities |
| Forms | react-hook-form |
| HTTP | Native `fetch` via typed client |
| Testing | Jest + React Testing Library |

### Module Structure

```
frontend/
├── app/                # Next.js App Router pages
│   ├── layout.tsx      # Root layout (Navbar + footer + ErrorBoundary)
│   ├── page.tsx        # Dashboard
│   ├── books/page.tsx
│   ├── members/page.tsx
│   ├── borrow/page.tsx
│   ├── return/page.tsx
│   └── loans/
│       ├── page.tsx
│       └── overdue/page.tsx
├── components/
│   ├── layout/Navbar.tsx
│   ├── ui/             # Spinner, Alert, Modal, DataTable, ErrorBoundary
│   ├── books/          # BookForm
│   ├── members/        # MemberForm
│   └── loans/          # BorrowForm, ReturnForm
├── lib/
│   ├── types.ts        # Shared TypeScript domain types
│   ├── api/            # client.ts, books.ts, members.ts, loans.ts
│   └── constants.ts    # Centralized API endpoint constants
└── __tests__/          # Jest test suites
```

### API Routing Strategy

Next.js is configured with API rewrites in `next.config.js`:

```
/api/* → http://backend:8000/api/*   (Docker-internal)
/api/* → $NEXT_PUBLIC_API_BASE_URL/* (Override for local dev)
```

This means the frontend never hard-codes a backend URL — all `fetch` calls go to `/api/v1/...` and Next.js proxies them.

## Data Flow — Borrow a Book

```
Browser
  → POST /api/v1/loans/borrow (Next.js rewrite proxy)
    → FastAPI router (loans.py)
      → LoanService.borrow()
        → LoanRepository (SELECT FOR UPDATE on Book)
        → BookRepository.decrement_available()
        → LoanRepository.create()
      → LoanResponse serialized
  ← 201 Created
```

## Fine Calculation

```python
def calculate_fine(due_at, returned_at, rate_per_day):
    delta = returned_at - due_at
    overdue_days = delta.days + (1 if delta.seconds > 0 else 0)
    return round_half_up(overdue_days * rate_per_day)
```

Default rate: **$0.50/day** (configurable via `FINE_RATE_PER_DAY` env var).
