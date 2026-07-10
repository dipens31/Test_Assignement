import uuid
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.loan import LoanDetailResponse
from app.services.loan_service import LoanService

router = APIRouter(prefix="/members", tags=["Members"])


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
    return svc.get_member_loans(member_id, active_only=active_only)
