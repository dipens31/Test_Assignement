import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


def trim_and_validate_string(value: str) -> str:
    """Trim whitespace and validate that string is not empty after trimming."""
    if value is None:
        return value
    trimmed = value.strip()
    if not trimmed:
        raise ValueError("Field cannot be empty or whitespace only")
    return trimmed


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, examples=["The Pragmatic Programmer"])
    author: str = Field(..., min_length=1, max_length=300, examples=["David Thomas"])
    isbn: Optional[str] = Field(default=None, max_length=20, examples=["978-0-13-595705-9"])
    published_year: Optional[int] = Field(default=None, ge=1000, le=9999, examples=[1999])
    copies_total: int = Field(default=1, ge=1, examples=[3])

    @field_validator('title', 'author')
    @classmethod
    def validate_strings(cls, v: str) -> str:
        return trim_and_validate_string(v)

    @field_validator('isbn')
    @classmethod
    def validate_isbn(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return trim_and_validate_string(v)
        return v


class BookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    author: Optional[str] = Field(default=None, min_length=1, max_length=300)
    isbn: Optional[str] = Field(default=None, max_length=20)
    published_year: Optional[int] = Field(default=None, ge=1000, le=9999)
    copies_total: Optional[int] = Field(default=None, ge=1)

    @field_validator('title', 'author', 'isbn')
    @classmethod
    def validate_strings(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return trim_and_validate_string(v)
        return v


class BookResponse(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    isbn: Optional[str]
    published_year: Optional[int]
    copies_total: int
    copies_available: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
