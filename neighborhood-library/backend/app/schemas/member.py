import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class MemberCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=300, examples=["Alice Johnson"])
    email: EmailStr = Field(..., examples=["alice@example.com"])
    phone: Optional[str] = Field(default=None, max_length=50, examples=["+1-555-0100"])
    address: Optional[str] = Field(default=None, max_length=500, examples=["123 Main St, Springfield"])


class MemberUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=300)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = Field(default=None, max_length=500)


class MemberResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    phone: Optional[str]
    address: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
