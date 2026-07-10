import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session, joinedload

from app.models.loan import Loan, LoanStatus


class LoanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        member_id: uuid.UUID,
        book_id: uuid.UUID,
        borrowed_at: datetime,
        due_at: Optional[datetime],
    ) -> Loan:
        loan = Loan(
            member_id=member_id,
            book_id=book_id,
            borrowed_at=borrowed_at,
            due_at=due_at,
            status=LoanStatus.BORROWED,
            fine_amount=0,
        )
        self.db.add(loan)
        self.db.commit()
        self.db.refresh(loan)
        return loan

    def get_by_id(self, loan_id: uuid.UUID) -> Optional[Loan]:
        return (
            self.db.query(Loan)
            .options(joinedload(Loan.member), joinedload(Loan.book))
            .filter(Loan.id == loan_id)
            .first()
        )

    def get_by_id_for_update(self, loan_id: uuid.UUID) -> Optional[Loan]:
        return self.db.query(Loan).filter(Loan.id == loan_id).with_for_update().first()

    def get_active_loan_for_member_book(
        self, member_id: uuid.UUID, book_id: uuid.UUID
    ) -> Optional[Loan]:
        return (
            self.db.query(Loan)
            .filter(
                Loan.member_id == member_id,
                Loan.book_id == book_id,
                Loan.status.in_([LoanStatus.BORROWED, LoanStatus.OVERDUE]),
            )
            .first()
        )

    def list(
        self,
        skip: int = 0,
        limit: int = 20,
        member_id: Optional[uuid.UUID] = None,
        book_id: Optional[uuid.UUID] = None,
        status: Optional[LoanStatus] = None,
    ) -> Tuple[int, List[Loan]]:
        query = self.db.query(Loan).options(
            joinedload(Loan.member), joinedload(Loan.book)
        )

        if member_id:
            query = query.filter(Loan.member_id == member_id)
        if book_id:
            query = query.filter(Loan.book_id == book_id)
        if status:
            query = query.filter(Loan.status == status)

        total = query.count()
        items = query.order_by(Loan.borrowed_at.desc()).offset(skip).limit(limit).all()
        return total, items

    def get_overdue(self, now: datetime) -> List[Loan]:
        return (
            self.db.query(Loan)
            .options(joinedload(Loan.member), joinedload(Loan.book))
            .filter(
                Loan.status == LoanStatus.BORROWED,
                Loan.due_at.isnot(None),
                Loan.due_at < now,
            )
            .order_by(Loan.due_at)
            .all()
        )

    def save(self, loan: Loan) -> Loan:
        self.db.commit()
        self.db.refresh(loan)
        return loan
