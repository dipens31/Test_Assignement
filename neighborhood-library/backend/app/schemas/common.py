from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    skip: int
    limit: int
    items: List[T]


class ErrorResponse(BaseModel):
    detail: str
