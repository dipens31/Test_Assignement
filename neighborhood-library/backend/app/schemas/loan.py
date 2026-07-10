import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.loan import LoanStatus
from app.schemas.book import BookResponse
from app.schemas.member import MemberResponse


class BorrowRequest(BaseModel):
    member_id: uuid.UUID = Field(..., examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890"])
    book_id: uuid.UUID = Field(..., examples=["b2c3d4e5-f6a7-8901-bcde-f12345678901"])
    due_at: Optional[datetime] = Field(
        default=None,
        examples=["2025-08-01T00:00:00Z"],
        description="Optional due date for the loan. If omitted the library staff sets it later.",
    )

    @field_validator('due_at')
    @classmethod
    def validate_due_at(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None:
            now = datetime.now(datetime.now().astimezone().tzinfo)
            if v.tzinfo is None:
                v = v.replace(tzinfo=now.tzinfo)
            if v <= now:
                raise ValueError("due_at must be a future datetime")
        return v


class ReturnRequest(BaseModel):
    loan_id: uuid.UUID = Field(..., examples=["c3d4e5f6-a7b8-9012-cdef-123456789012"])


class LoanResponse(BaseModel):
    id: uuid.UUID
    member_id: uuid.UUID
    book_id: uuid.UUID
    borrowed_at: datetime
    due_at: Optional[datetime]
    returned_at: Optional[datetime]
    status: LoanStatus
    fine_amount: Decimal

    model_config = {"from_attributes": True}


class LoanDetailResponse(LoanResponse):
    """Full loan with nested member and book details."""

    member: MemberResponse
    book: BookResponse

    model_config = {"from_attributes": True}
