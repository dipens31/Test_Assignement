"""Idempotent seed script — runs after `alembic upgrade head`.

Creates 8 books, 5 members, and 6 loans covering BORROWED / RETURNED / OVERDUE states
so the app is immediately useful when someone first starts it with docker compose.
"""

import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Allow running from any CWD
sys.path.insert(0, os.path.dirname(__file__))

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://library_user:library_password@db:5432/library",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)

FINE_RATE = float(os.getenv("FINE_RATE_PER_DAY", "0.50"))

now = datetime.now(timezone.utc)


def overdue_fine(due_at: datetime) -> Decimal:
    delta = now - due_at
    days = delta.days + (1 if delta.seconds > 0 else 0)
    if days <= 0:
        return Decimal("0.00")
    return (Decimal(str(days)) * Decimal(str(FINE_RATE))).quantize(Decimal("0.01"))


def seed():
    with Session() as db:
        # ── Guard: skip if data already present ──────────────────────────────────
        existing = db.execute(text("SELECT COUNT(*) FROM books")).scalar()
        if existing and existing > 0:
            print(f"[seed] Database already has {existing} book(s). Skipping seed.")
            return

        print("[seed] Seeding database …")

        # ── Books ─────────────────────────────────────────────────────────────────
        book_ids = [str(uuid.uuid4()) for _ in range(8)]
        books = [
            {
                "id": book_ids[0],
                "title": "The Pragmatic Programmer",
                "author": "David Thomas, Andrew Hunt",
                "isbn": "9780135957059",
                "published_year": 2019,
                "copies_total": 3,
                "copies_available": 2,
            },
            {
                "id": book_ids[1],
                "title": "Clean Code",
                "author": "Robert C. Martin",
                "isbn": "9780132350884",
                "published_year": 2008,
                "copies_total": 2,
                "copies_available": 1,
            },
            {
                "id": book_ids[2],
                "title": "Design Patterns",
                "author": "Gang of Four",
                "isbn": "9780201633610",
                "published_year": 1994,
                "copies_total": 2,
                "copies_available": 1,
            },
            {
                "id": book_ids[3],
                "title": "Introduction to Algorithms",
                "author": "Cormen, Leiserson, Rivest, Stein",
                "isbn": "9780262033848",
                "published_year": 2009,
                "copies_total": 3,
                "copies_available": 3,
            },
            {
                "id": book_ids[4],
                "title": "The Mythical Man-Month",
                "author": "Frederick P. Brooks Jr.",
                "isbn": "9780201835953",
                "published_year": 1995,
                "copies_total": 1,
                "copies_available": 0,
            },
            {
                "id": book_ids[5],
                "title": "Refactoring",
                "author": "Martin Fowler",
                "isbn": "9780134757599",
                "published_year": 2018,
                "copies_total": 2,
                "copies_available": 2,
            },
            {
                "id": book_ids[6],
                "title": "The Phoenix Project",
                "author": "Gene Kim, Kevin Behr, George Spafford",
                "isbn": "9781942788294",
                "published_year": 2014,
                "copies_total": 2,
                "copies_available": 1,
            },
            {
                "id": book_ids[7],
                "title": "Designing Data-Intensive Applications",
                "author": "Martin Kleppmann",
                "isbn": "9781449373320",
                "published_year": 2017,
                "copies_total": 2,
                "copies_available": 2,
            },
        ]

        for b in books:
            db.execute(
                text(
                    "INSERT INTO books (id,title,author,isbn,published_year,copies_total,copies_available,created_at,updated_at) "
                    "VALUES (:id,:title,:author,:isbn,:published_year,:copies_total,:copies_available,now(),now())"
                ),
                b,
            )

        # ── Members ───────────────────────────────────────────────────────────────
        member_ids = [str(uuid.uuid4()) for _ in range(5)]
        members = [
            {"id": member_ids[0], "name": "Alice Johnson",  "email": "alice@example.com",  "phone": "+1-555-0101", "address": "123 Main Street, Springfield"},
            {"id": member_ids[1], "name": "Bob Smith",      "email": "bob@example.com",    "phone": "+1-555-0102", "address": "456 Oak Avenue, Shelbyville"},
            {"id": member_ids[2], "name": "Carol Davis",    "email": "carol@example.com",  "phone": "+1-555-0103", "address": "789 Pine Road, Capital City"},
            {"id": member_ids[3], "name": "David Wilson",   "email": "david@example.com",  "phone": "+1-555-0104", "address": "321 Elm Street, Ogdenville"},
            {"id": member_ids[4], "name": "Eva Martinez",   "email": "eva@example.com",    "phone": "+1-555-0105", "address": "654 Maple Drive, North Haverbrook"},
        ]

        for m in members:
            db.execute(
                text(
                    "INSERT INTO members (id,name,email,phone,address,created_at,updated_at) "
                    "VALUES (:id,:name,:email,:phone,:address,now(),now())"
                ),
                m,
            )

        # ── Loans ─────────────────────────────────────────────────────────────────
        # 1. Alice  — BORROWED  (Clean Code, due in 7 days)
        # 2. Bob    — BORROWED  (The Pragmatic Programmer, due in 14 days)
        # 3. Carol  — OVERDUE   (The Mythical Man-Month, was due 5 days ago → $2.50 fine)
        # 4. David  — OVERDUE   (The Phoenix Project, was due 12 days ago → $6.00 fine)
        # 5. Eva    — RETURNED  (Design Patterns, returned 2 days ago, no fine)
        # 6. Alice  — RETURNED  (Refactoring, returned late, $1.00 fine)

        carol_due   = now - timedelta(days=5)
        david_due   = now - timedelta(days=12)

        loans = [
            {
                "id": str(uuid.uuid4()),
                "member_id": member_ids[0],  # Alice
                "book_id":   book_ids[1],    # Clean Code
                "borrowed_at": now - timedelta(days=3),
                "due_at":    now + timedelta(days=7),
                "returned_at": None,
                "status": "BORROWED",
                "fine_amount": Decimal("0.00"),
            },
            {
                "id": str(uuid.uuid4()),
                "member_id": member_ids[1],  # Bob
                "book_id":   book_ids[0],    # The Pragmatic Programmer
                "borrowed_at": now - timedelta(days=1),
                "due_at":    now + timedelta(days=14),
                "returned_at": None,
                "status": "BORROWED",
                "fine_amount": Decimal("0.00"),
            },
            {
                "id": str(uuid.uuid4()),
                "member_id": member_ids[2],  # Carol
                "book_id":   book_ids[4],    # The Mythical Man-Month
                "borrowed_at": now - timedelta(days=19),
                "due_at":    carol_due,
                "returned_at": None,
                "status": "BORROWED",
                "fine_amount": Decimal("0.00"),
            },
            {
                "id": str(uuid.uuid4()),
                "member_id": member_ids[3],  # David
                "book_id":   book_ids[6],    # The Phoenix Project
                "borrowed_at": now - timedelta(days=26),
                "due_at":    david_due,
                "returned_at": None,
                "status": "BORROWED",
                "fine_amount": Decimal("0.00"),
            },
            {
                "id": str(uuid.uuid4()),
                "member_id": member_ids[4],  # Eva
                "book_id":   book_ids[2],    # Design Patterns
                "borrowed_at": now - timedelta(days=10),
                "due_at":    now - timedelta(days=3),
                "returned_at": now - timedelta(days=2),
                "status": "RETURNED",
                "fine_amount": Decimal("0.00"),
            },
            {
                "id": str(uuid.uuid4()),
                "member_id": member_ids[0],  # Alice (2nd loan)
                "book_id":   book_ids[5],    # Refactoring (but copies_available=2 → stays OK)
                "borrowed_at": now - timedelta(days=20),
                "due_at":    now - timedelta(days=6),
                "returned_at": now - timedelta(days=4),
                "status": "RETURNED",
                "fine_amount": Decimal("1.00"),
            },
        ]

        for ln in loans:
            db.execute(
                text(
                    "INSERT INTO loans (id,member_id,book_id,borrowed_at,due_at,returned_at,status,fine_amount,created_at,updated_at) "
                    "VALUES (:id,:member_id,:book_id,:borrowed_at,:due_at,:returned_at,CAST(:status AS loan_status),:fine_amount,now(),now())"
                ),
                ln,
            )

        db.commit()
        print("[seed] Done — 8 books, 5 members, 6 loans created.")


if __name__ == "__main__":
    seed()
