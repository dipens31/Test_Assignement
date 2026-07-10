import uuid
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import get_logger
from app.schemas.loan import LoanDetailResponse
from app.services.loan_service import LoanService

router = APIRouter(prefix="/members", tags=["Members"])
logger = get_logger(__name__)


def get_loan_service(db: Session = Depends(get_db)) -> LoanService:
    return LoanService(db)


@router.get(
    "/{member_id}/loans",
    response_model=List[LoanDetailResponse],
    summary="List all loans for a specific member",
)
def get_member_loans(
    member_id: uuid.UUID,
    active_only: bool = Query(default=False, description="Return only currently borrowed books"),
    svc: LoanService = Depends(get_loan_service),
):
    logger.info(f"API: Get member loans request - member_id: {member_id}, active_only: {active_only}")
    try:
        result = svc.get_member_loans(member_id, active_only=active_only)
        logger.info(f"API: Returning {len(result)} loans for member_id: {member_id}")
        return result
    except Exception as e:
        logger.error(f"API: Error getting loans for member {member_id} - {str(e)}")
        raise
