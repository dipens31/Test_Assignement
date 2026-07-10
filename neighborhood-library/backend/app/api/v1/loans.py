import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import get_logger
from app.models.loan import LoanStatus
from app.schemas.common import PaginatedResponse
from app.schemas.loan import BorrowRequest, LoanDetailResponse, LoanResponse, ReturnRequest
from app.services.loan_service import LoanService

router = APIRouter(prefix="/loans", tags=["Loans"])
logger = get_logger(__name__)


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
    logger.info(f"API: Borrow book request - member_id: {payload.member_id}, book_id: {payload.book_id}")
    try:
        result = svc.borrow(payload)
        logger.info(f"API: Book borrowed successfully - loan_id: {result.id}")
        return result
    except Exception as e:
        logger.error(f"API: Error borrowing book - {str(e)}")
        raise


@router.post(
    "/return",
    response_model=LoanDetailResponse,
    summary="Return a borrowed book",
)
def return_book(
    payload: ReturnRequest,
    svc: LoanService = Depends(get_loan_service),
):
    logger.info(f"API: Return book request - loan_id: {payload.loan_id}")
    try:
        result = svc.return_book(payload)
        logger.info(f"API: Book returned successfully - loan_id: {payload.loan_id}")
        return result
    except Exception as e:
        logger.error(f"API: Error returning book - {str(e)}")
        raise


@router.get(
    "/overdue",
    response_model=List[LoanDetailResponse],
    summary="List all currently overdue loans with calculated fines",
)
def list_overdue_loans(
    svc: LoanService = Depends(get_loan_service),
):
    logger.info("API: List overdue loans request")
    try:
        result = svc.get_overdue()
        logger.info(f"API: Returning {len(result)} overdue loans")
        return result
    except Exception as e:
        logger.error(f"API: Error listing overdue loans - {str(e)}")
        raise


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
    logger.info(f"API: List loans request - skip: {skip}, limit: {limit}")
    total, items = svc.list(
        skip=skip, limit=limit, member_id=member_id, book_id=book_id, status=status
    )
    logger.info(f"API: Returning {len(items)} loans")
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
    logger.info(f"API: Get loan request - ID: {loan_id}")
    try:
        result = svc.get_loan(loan_id)
        logger.info(f"API: Loan retrieved successfully - ID: {loan_id}")
        return result
    except Exception as e:
        logger.error(f"API: Error getting loan {loan_id} - {str(e)}")
        raise
