"""Initial schema: books, members, loans

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── loan_status enum ────────────────────────────────────────────────────
    loan_status_enum = postgresql.ENUM(
        "BORROWED", "RETURNED", "OVERDUE", name="loan_status", create_type=False
    )
    loan_status_enum.create(op.get_bind(), checkfirst=True)

    # ── books ────────────────────────────────────────────────────────────────
    op.create_table(
        "books",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("author", sa.String(300), nullable=False),
        sa.Column("isbn", sa.String(20), unique=True, nullable=True),
        sa.Column("published_year", sa.Integer, nullable=True),
        sa.Column("copies_total", sa.Integer, nullable=False, server_default="1"),
        sa.Column("copies_available", sa.Integer, nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("copies_total >= 1", name="ck_books_copies_total_positive"),
        sa.CheckConstraint("copies_available >= 0", name="ck_books_copies_available_non_negative"),
        sa.CheckConstraint(
            "copies_available <= copies_total",
            name="ck_books_copies_available_lte_total",
        ),
    )
    op.create_index("ix_books_title", "books", ["title"])
    op.create_index("ix_books_author", "books", ["author"])
    op.create_index("ix_books_isbn", "books", ["isbn"])

    # ── members ──────────────────────────────────────────────────────────────
    op.create_table(
        "members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("email", sa.String(320), unique=True, nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_members_name", "members", ["name"])
    op.create_index("ix_members_email", "members", ["email"])

    # ── loans ────────────────────────────────────────────────────────────────
    op.create_table(
        "loans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "member_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("members.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "book_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("books.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("borrowed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("returned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM("BORROWED", "RETURNED", "OVERDUE", name="loan_status", create_type=False),
            nullable=False,
            server_default="BORROWED",
        ),
        sa.Column("fine_amount", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_loans_member_id", "loans", ["member_id"])
    op.create_index("ix_loans_book_id", "loans", ["book_id"])
    op.create_index("ix_loans_status", "loans", ["status"])


def downgrade() -> None:
    op.drop_table("loans")
    op.drop_table("members")
    op.drop_table("books")
    op.execute("DROP TYPE IF EXISTS loan_status")
