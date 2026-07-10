import uuid
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.member import Member


class MemberRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, email: str, phone: Optional[str], address: Optional[str]) -> Member:
        member = Member(name=name, email=email, phone=phone, address=address)
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def get_by_id(self, member_id: uuid.UUID) -> Optional[Member]:
        return self.db.query(Member).filter(Member.id == member_id).first()

    def get_by_email(self, email: str) -> Optional[Member]:
        return self.db.query(Member).filter(Member.email == email).first()

    def list(
        self,
        skip: int = 0,
        limit: int = 20,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Tuple[int, List[Member]]:
        query = self.db.query(Member)

        if name:
            query = query.filter(Member.name.ilike(f"%{name}%"))
        if email:
            query = query.filter(Member.email.ilike(f"%{email}%"))

        total = query.count()
        items = query.order_by(Member.name).offset(skip).limit(limit).all()
        return total, items

    def update(self, member: Member, **kwargs) -> Member:
        for key, value in kwargs.items():
            if value is not None:
                setattr(member, key, value)
        self.db.commit()
        self.db.refresh(member)
        return member

    def delete(self, member: Member) -> None:
        self.db.delete(member)
        self.db.commit()
