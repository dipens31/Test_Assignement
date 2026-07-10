import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import get_logger
from app.schemas.common import PaginatedResponse
from app.schemas.member import MemberCreate, MemberResponse, MemberUpdate
from app.services.member_service import MemberService

router = APIRouter(prefix="/members", tags=["Members"])
logger = get_logger(__name__)


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
    logger.info(f"API: Create member request - email: {payload.email}")
    try:
        result = svc.create(payload)
        logger.info(f"API: Member created successfully - ID: {result.id}")
        return result
    except Exception as e:
        logger.error(f"API: Error creating member - {str(e)}")
        raise


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
    logger.info(f"API: List members request - skip: {skip}, limit: {limit}")
    total, items = svc.list(skip=skip, limit=limit, name=name, email=email)
    logger.info(f"API: Returning {len(items)} members")
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
    logger.info(f"API: Get member request - ID: {member_id}")
    try:
        result = svc.get(member_id)
        logger.info(f"API: Member retrieved successfully - ID: {member_id}")
        return result
    except Exception as e:
        logger.error(f"API: Error getting member {member_id} - {str(e)}")
        raise


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
    logger.info(f"API: Update member request - ID: {member_id}")
    try:
        result = svc.update(member_id, payload)
        logger.info(f"API: Member updated successfully - ID: {member_id}")
        return result
    except Exception as e:
        logger.error(f"API: Error updating member {member_id} - {str(e)}")
        raise
