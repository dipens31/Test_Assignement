import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class LoanStatus(str, enum.Enum):
    BORROWED = "BORROWED"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"


class Loan(TimestampMixin, Base):
    __tablename__ = "loans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("members.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("books.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    borrowed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[LoanStatus] = mapped_column(
        Enum(LoanStatus, name="loan_status"), nullable=False, default=LoanStatus.BORROWED, index=True
    )
    fine_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    member: Mapped["Member"] = relationship("Member", back_populates="loans")  # noqa: F821
    book: Mapped["Book"] = relationship("Book", back_populates="loans")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Loan id={self.id} member={self.member_id} book={self.book_id} status={self.status}>"
