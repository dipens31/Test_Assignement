import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.member import MemberCreate, MemberResponse, MemberUpdate
from app.services.member_service import MemberService

router = APIRouter(prefix="/members", tags=["Members"])


def get_member_service(db: Session = Depends(get_db)) -> MemberService:
    return MemberService(db)


@router.post(
    "",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new library member",
)
def create_member(
    payload: MemberCreate,
    svc: MemberService = Depends(get_member_service),
):
    return svc.create(payload)


@router.get(
    "",
    response_model=PaginatedResponse[MemberResponse],
    summary="List / search members",
)
def list_members(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    name: Optional[str] = Query(default=None, description="Partial name search"),
    email: Optional[str] = Query(default=None, description="Partial email search"),
    svc: MemberService = Depends(get_member_service),
):
    total, items = svc.list(skip=skip, limit=limit, name=name, email=email)
    return PaginatedResponse(total=total, skip=skip, limit=limit, items=items)


@router.get(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Get a single member by ID",
)
def get_member(
    member_id: uuid.UUID,
    svc: MemberService = Depends(get_member_service),
):
    return svc.get(member_id)


@router.put(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Update an existing member",
)
def update_member(
    member_id: uuid.UUID,
    payload: MemberUpdate,
    svc: MemberService = Depends(get_member_service),
):
    return svc.update(member_id, payload)
