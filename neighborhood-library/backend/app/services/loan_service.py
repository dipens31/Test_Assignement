import uuid
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.core.logging import get_logger
from app.models.loan import Loan, LoanStatus
from app.repositories.book_repository import BookRepository
from app.repositories.loan_repository import LoanRepository
from app.repositories.member_repository import MemberRepository
from app.schemas.loan import BorrowRequest, ReturnRequest

logger = get_logger(__name__)


def calculate_fine(due_at: datetime, returned_at: datetime, rate_per_day: float) -> Decimal:
    """
    Calculate a fine for an overdue loan.

    Rules:
    - If the book is returned on or before the due date, no fine.
    - Any partial day overdue counts as a full day (ceiling).
    - Fine = overdue_days * rate_per_day, rounded to 2 decimal places.
    """
    if returned_at <= due_at:
        return Decimal("0.00")

    delta = returned_at - due_at
    # ceil to nearest full day
    overdue_days = delta.days + (1 if delta.seconds > 0 else 0)
    raw = Decimal(str(overdue_days)) * Decimal(str(rate_per_day))
    return raw.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class LoanService:
    def __init__(self, db: Session):
        self.db = db
        self.loan_repo = LoanRepository(db)
        self.book_repo = BookRepository(db)
        self.member_repo = MemberRepository(db)

    def borrow(self, payload: BorrowRequest) -> Loan:
        logger.info(f"Borrowing book - member_id: {payload.member_id}, book_id: {payload.book_id}")
        member = self.member_repo.get_by_id(payload.member_id)
        if not member:
            logger.warning(f"Member not found with ID: {payload.member_id}")
            raise NotFoundError("Member", str(payload.member_id))

        # Check if member already has an active loan for this book
        existing_active_loan = self.loan_repo.get_active_loan_for_member_book(payload.member_id, payload.book_id)
        if existing_active_loan:
            logger.warning(f"Member {payload.member_id} already has an active loan for book {payload.book_id}")
            raise ConflictError("Member already has an active loan for this book. Please return it before borrowing again.")

        # Lock the book row to prevent concurrent over-borrowing
        book = self.book_repo.get_by_id_for_update(payload.book_id)
        if not book:
            logger.warning(f"Book not found with ID: {payload.book_id}")
            raise NotFoundError("Book", str(payload.book_id))

        if book.copies_available <= 0:
            logger.warning(f"Book unavailable - no copies left for book_id: {payload.book_id}")
            raise ConflictError("Book currently unavailable — no copies left to borrow.")

        # Validate due_at is in the future if provided
        if payload.due_at:
            now = datetime.now(timezone.utc)
            due = payload.due_at
            # normalise to tz-aware
            if due.tzinfo is None:
                due = due.replace(tzinfo=timezone.utc)
            if due <= now:
                logger.warning(f"Invalid due_at - must be future datetime: {payload.due_at}")
                raise BadRequestError("due_at must be a future datetime.")

        book.copies_available -= 1

        loan = self.loan_repo.create(
            member_id=payload.member_id,
            book_id=payload.book_id,
            borrowed_at=datetime.now(timezone.utc),
            due_at=payload.due_at,
        )
        logger.info(f"Successfully created loan with ID: {loan.id}")
        return loan

    def return_book(self, payload: ReturnRequest) -> Loan:
        logger.info(f"Returning book - loan_id: {payload.loan_id}")
        # Lock the loan row for atomic update
        loan = self.loan_repo.get_by_id_for_update(payload.loan_id)
        if not loan:
            logger.warning(f"Loan not found with ID: {payload.loan_id}")
            raise NotFoundError("Loan", str(payload.loan_id))

        if loan.status == LoanStatus.RETURNED:
            logger.warning(f"Loan already returned - loan_id: {payload.loan_id}")
            raise BadRequestError("This book has already been returned.")

        now = datetime.now(timezone.utc)
        loan.returned_at = now
        loan.status = LoanStatus.RETURNED

        # Calculate fine if overdue
        if loan.due_at:
            due = loan.due_at
            if due.tzinfo is None:
                due = due.replace(tzinfo=timezone.utc)
            if now > due:
                fine = calculate_fine(due, now, settings.FINE_RATE_PER_DAY)
                loan.fine_amount = float(fine)
                logger.info(f"Loan overdue - loan_id: {payload.loan_id}, fine: ${fine}")
                loan.status = LoanStatus.RETURNED  # still RETURNED, fine recorded

        # Release the copy — lock the book row too
        book = self.book_repo.get_by_id_for_update(loan.book_id)
        if book:
            book.copies_available += 1

        returned_loan = self.loan_repo.save(loan)
        logger.info(f"Successfully returned loan - loan_id: {payload.loan_id}")
        return returned_loan

    def get_loan(self, loan_id: uuid.UUID) -> Loan:
        logger.info(f"Fetching loan with ID: {loan_id}")
        loan = self.loan_repo.get_by_id(loan_id)
        if not loan:
            logger.warning(f"Loan not found with ID: {loan_id}")
            raise NotFoundError("Loan", str(loan_id))
        logger.info(f"Successfully fetched loan with ID: {loan_id}")
        return loan

    def list(
        self,
        skip: int = 0,
        limit: int = 20,
        member_id: Optional[uuid.UUID] = None,
        book_id: Optional[uuid.UUID] = None,
        status: Optional[LoanStatus] = None,
    ) -> Tuple[int, List[Loan]]:
        logger.info(f"Listing loans with filters - skip: {skip}, limit: {limit}, member_id: {member_id}, book_id: {book_id}, status: {status}")
        total, items = self.loan_repo.list(
            skip=skip, limit=limit, member_id=member_id, book_id=book_id, status=status
        )
        logger.info(f"Found {total} loans, returning {len(items)} items")
        return total, items

    def get_member_loans(
        self,
        member_id: uuid.UUID,
        active_only: bool = False,
    ) -> List[Loan]:
        logger.info(f"Fetching loans for member_id: {member_id}, active_only: {active_only}")
        member = self.member_repo.get_by_id(member_id)
        if not member:
            logger.warning(f"Member not found with ID: {member_id}")
            raise NotFoundError("Member", str(member_id))

        status = LoanStatus.BORROWED if active_only else None
        _, loans = self.loan_repo.list(member_id=member_id, status=status, limit=1000)
        logger.info(f"Found {len(loans)} loans for member_id: {member_id}")
        return loans

    def get_overdue(self) -> List[Loan]:
        logger.info("Fetching overdue loans")
        now = datetime.now(timezone.utc)
        loans = self.loan_repo.get_overdue(now)
        # Annotate in-memory with current fine estimate (not yet persisted)
        for loan in loans:
            loan.status = LoanStatus.OVERDUE
            if loan.due_at:
                due = loan.due_at
                if due.tzinfo is None:
                    due = due.replace(tzinfo=timezone.utc)
                loan.fine_amount = float(
                    calculate_fine(due, now, settings.FINE_RATE_PER_DAY)
                )
        logger.info(f"Found {len(loans)} overdue loans")
        return loans
