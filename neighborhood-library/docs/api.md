# API Reference

Base URL: `http://localhost:8000/api/v1`

Interactive docs: `http://localhost:8000/docs` (Swagger UI)

---

## Books

### `GET /books`

List books with optional filters and pagination.

**Query Parameters**

| Param | Type | Description |
|---|---|---|
| `title` | string | Case-insensitive partial match |
| `author` | string | Case-insensitive partial match |
| `isbn` | string | Exact match |
| `available_only` | boolean | Only books with `copies_available > 0` |
| `skip` | integer | Offset (default 0) |
| `limit` | integer | Max results (default 20, max 100) |

**Response** `200 OK`

```json
{
  "total": 42,
  "skip": 0,
  "limit": 20,
  "items": [
    {
      "id": "uuid",
      "title": "Clean Code",
      "author": "Robert C. Martin",
      "isbn": "978-0-13-235088-4",
      "published_year": 2008,
      "copies_total": 3,
      "copies_available": 2,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### `POST /books`

Create a new book.

**Request Body**

```json
{
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "isbn": "978-0-13-235088-4",
  "published_year": 2008,
  "copies_total": 3
}
```

**Response** `201 Created` — `BookResponse`

**Errors**
- `409 Conflict` — ISBN already exists

---

### `GET /books/{book_id}`

Get a single book by UUID.

**Response** `200 OK` — `BookResponse`

**Errors**
- `404 Not Found`

---

### `PUT /books/{book_id}`

Update book fields (partial update supported).

**Request Body** — same as `POST /books` but all fields optional

**Response** `200 OK` — `BookResponse`

---

## Members

### `GET /members`

List members with optional name/email filter.

**Query Parameters**

| Param | Type | Description |
|---|---|---|
| `name` | string | Case-insensitive partial match |
| `email` | string | Case-insensitive partial match |
| `skip` | integer | |
| `limit` | integer | |

**Response** `200 OK` — `PaginatedResponse<MemberResponse>`

---

### `POST /members`

Register a new member.

**Request Body**

```json
{
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "phone": "+1-555-0100",
  "address": "123 Main St"
}
```

**Response** `201 Created`

**Errors**
- `409 Conflict` — Email already registered

---

### `GET /members/{member_id}`

**Response** `200 OK` — `MemberResponse`

---

### `PUT /members/{member_id}`

**Response** `200 OK` — `MemberResponse`

---

### `GET /members/{member_id}/loans`

List all loans for a specific member.

**Query Parameters**

| Param | Type | Description |
|---|---|---|
| `active_only` | boolean | Only BORROWED/OVERDUE loans |

**Response** `200 OK` — `list[LoanResponse]`

---

## Loans

### `GET /loans`

List all loans.

**Query Parameters**

| Param | Type | Description |
|---|---|---|
| `status` | string | `BORROWED`, `RETURNED`, or `OVERDUE` |
| `member_id` | UUID | Filter by member |
| `book_id` | UUID | Filter by book |
| `skip` | integer | |
| `limit` | integer | |

**Response** `200 OK` — `PaginatedResponse<LoanDetailResponse>`

---

### `POST /loans/borrow`

Check out a book for a member.

**Request Body**

```json
{
  "member_id": "uuid",
  "book_id": "uuid",
  "due_at": "2025-02-01T00:00:00Z"
}
```

`due_at` is optional — defaults to 14 days from now.

**Response** `201 Created` — `LoanResponse`

**Errors**
- `404 Not Found` — Member or book not found
- `409 Conflict` — No copies available OR member already has an active loan for this book

---

### `POST /loans/return`

Return a borrowed book. Calculates and stores fine if overdue.

**Request Body**

```json
{
  "loan_id": "uuid"
}
```

**Response** `200 OK` — `LoanResponse`

```json
{
  "id": "uuid",
  "member_id": "uuid",
  "book_id": "uuid",
  "status": "RETURNED",
  "borrowed_at": "2024-12-01T00:00:00Z",
  "due_at": "2024-12-15T00:00:00Z",
  "returned_at": "2024-12-20T00:00:00Z",
  "fine_amount": "2.50"
}
```

**Errors**
- `404 Not Found` — Loan not found
- `400 Bad Request` — Loan already returned

---

### `GET /loans/overdue`

List all currently overdue loans.

**Response** `200 OK` — `list[LoanDetailResponse]`

---

### `GET /loans/{loan_id}`

Get a single loan by UUID.

**Response** `200 OK` — `LoanDetailResponse`

---

## Error Schema

All errors follow:

```json
{
  "detail": "Human-readable error message"
}
```

| Status | Meaning |
|---|---|
| `400` | Bad request (e.g., already returned) |
| `404` | Resource not found |
| `409` | Conflict (duplicate ISBN/email, no copies, duplicate loan) |
| `422` | Validation error (Pydantic - e.g., past due date, whitespace-only input) |
| `500` | Internal server error |

---

## Health Check

### `GET /health`

**Response** `200 OK`

```json
{ "status": "ok" }
```
