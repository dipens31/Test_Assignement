import uuid

from sqlalchemy import CheckConstraint, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Book(TimestampMixin, Base):
    __tablename__ = "books"
    __table_args__ = (
        CheckConstraint("copies_total >= 1", name="ck_books_copies_total_positive"),
        CheckConstraint("copies_available >= 0", name="ck_books_copies_available_non_negative"),
        CheckConstraint(
            "copies_available <= copies_total",
            name="ck_books_copies_available_lte_total",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    isbn: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True, index=True)
    published_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    copies_total: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    copies_available: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    loans: Mapped[list["Loan"]] = relationship("Loan", back_populates="book")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Book id={self.id} title={self.title!r}>"
