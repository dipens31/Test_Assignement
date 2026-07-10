# Database Schema

## Entity Relationship Diagram

```
┌──────────────┐         ┌──────────────┐         ┌───────────────┐
│   members    │         │    loans     │         │     books     │
├──────────────┤         ├──────────────┤         ├───────────────┤
│ id (PK)      │◀────────│ member_id FK │         │ id (PK)       │
│ name         │         │ id (PK)      │─────────▶│ title        │
│ email (UQ)   │         │ book_id FK   │         │ author        │
│ phone        │         │ borrowed_at  │         │ isbn (UQ)     │
│ address      │         │ due_at       │         │ published_year│
│ created_at   │         │ returned_at  │         │ copies_total  │
│ updated_at   │         │ status (enum)│         │ copies_avail  │
└──────────────┘         │ fine_amount  │         │ created_at    │
                         │ created_at   │         │ updated_at    │
                         │ updated_at   │         └───────────────┘
                         └──────────────┘
```

## Table Definitions

### `books`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `UUID` | PK | Generated via `uuid4` |
| `title` | `VARCHAR(500)` | NOT NULL, INDEX | |
| `author` | `VARCHAR(300)` | NOT NULL, INDEX | |
| `isbn` | `VARCHAR(20)` | UNIQUE, nullable, INDEX | |
| `published_year` | `INTEGER` | nullable | |
| `copies_total` | `INTEGER` | NOT NULL, ≥ 1 | Check constraint |
| `copies_available` | `INTEGER` | NOT NULL, ≥ 0, ≤ copies_total | Check constraints |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, server default NOW() | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, onupdate trigger | |

**Constraints:**
- `ck_books_copies_total_positive`: `copies_total >= 1`
- `ck_books_copies_available_non_negative`: `copies_available >= 0`
- `ck_books_copies_available_lte_total`: `copies_available <= copies_total`

### `members`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `UUID` | PK | |
| `name` | `VARCHAR(300)` | NOT NULL | |
| `email` | `VARCHAR(254)` | NOT NULL, UNIQUE, INDEX | |
| `phone` | `VARCHAR(30)` | nullable | |
| `address` | `TEXT` | nullable | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | |

### `loans`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `UUID` | PK | |
| `member_id` | `UUID` | FK → members.id, NOT NULL | |
| `book_id` | `UUID` | FK → books.id, NOT NULL | |
| `borrowed_at` | `TIMESTAMPTZ` | NOT NULL, server default | |
| `due_at` | `TIMESTAMPTZ` | NOT NULL | Default: borrowed_at + 14 days |
| `returned_at` | `TIMESTAMPTZ` | nullable | |
| `status` | `loan_status` | NOT NULL | Enum: BORROWED, RETURNED, OVERDUE |
| `fine_amount` | `NUMERIC(10,2)` | NOT NULL, default 0.00 | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | |

**Indexes:**
- `ix_loans_member_id`
- `ix_loans_book_id`
- `ix_loans_status`

### `loan_status` Enum

| Value | Description |
|---|---|
| `BORROWED` | Currently out on loan |
| `RETURNED` | Returned on time or with fine paid |
| `OVERDUE` | Past `due_at` and not returned |

## Migration History

| Revision | Description |
|---|---|
| `001_initial_schema` | Create `books`, `members`, `loans` tables + `loan_status` enum |

## Concurrency Notes

When processing a borrow request, the backend executes:

```sql
SELECT * FROM books WHERE id = :id FOR UPDATE;
```

This prevents two concurrent requests from over-borrowing the last available copy.
