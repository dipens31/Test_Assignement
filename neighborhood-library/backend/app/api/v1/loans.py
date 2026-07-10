import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.loan import LoanStatus
from app.schemas.common import PaginatedResponse
from app.schemas.loan import BorrowRequest, LoanDetailResponse, LoanResponse, ReturnRequest
from app.services.loan_service import LoanService

router = APIRouter(prefix="/loans", tags=["Loans"])


def get_loan_service(db: Session = Depends(get_db)) -> LoanService:
    return LoanService(db)


@router.post(
    "/borrow",
    response_model=LoanDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Borrow a book (member checks out a book)",
)
def borrow_book(
    payload: BorrowRequest,
    svc: LoanService = Depends(get_loan_service),
):
    return svc.borrow(payload)


@router.post(
    "/return",
    response_model=LoanDetailResponse,
    summary="Return a borrowed book",
)
def return_book(
    payload: ReturnRequest,
    svc: LoanService = Depends(get_loan_service),
):
    return svc.return_book(payload)


@router.get(
    "/overdue",
    response_model=List[LoanDetailResponse],
    summary="List all currently overdue loans with calculated fines",
)
def list_overdue_loans(
    svc: LoanService = Depends(get_loan_service),
):
    return svc.get_overdue()


@router.get(
    "",
    response_model=PaginatedResponse[LoanDetailResponse],
    summary="List loans with optional filters",
)
def list_loans(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    member_id: Optional[uuid.UUID] = Query(default=None),
    book_id: Optional[uuid.UUID] = Query(default=None),
    status: Optional[LoanStatus] = Query(default=None),
    svc: LoanService = Depends(get_loan_service),
):
    total, items = svc.list(
        skip=skip, limit=limit, member_id=member_id, book_id=book_id, status=status
    )
    return PaginatedResponse(total=total, skip=skip, limit=limit, items=items)


@router.get(
    "/{loan_id}",
    response_model=LoanDetailResponse,
    summary="Get a single loan by ID",
)
def get_loan(
    loan_id: uuid.UUID,
    svc: LoanService = Depends(get_loan_service),
):
    return svc.get_loan(loan_id)
