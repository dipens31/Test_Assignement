import uuid
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.member import Member
from app.repositories.member_repository import MemberRepository
from app.schemas.member import MemberCreate, MemberUpdate


class MemberService:
    def __init__(self, db: Session):
        self.repo = MemberRepository(db)

    def create(self, payload: MemberCreate) -> Member:
        existing = self.repo.get_by_email(str(payload.email))
        if existing:
            raise ConflictError(f"A member with email '{payload.email}' already exists.")
        return self.repo.create(
            name=payload.name,
            email=str(payload.email),
            phone=payload.phone,
            address=payload.address,
        )

    def get(self, member_id: uuid.UUID) -> Member:
        member = self.repo.get_by_id(member_id)
        if not member:
            raise NotFoundError("Member", str(member_id))
        return member

    def update(self, member_id: uuid.UUID, payload: MemberUpdate) -> Member:
        member = self.get(member_id)

        if payload.email and str(payload.email) != member.email:
            existing = self.repo.get_by_email(str(payload.email))
            if existing:
                raise ConflictError(f"A member with email '{payload.email}' already exists.")

        update_data = payload.model_dump(exclude_unset=True, exclude_none=True)
        if "email" in update_data:
            update_data["email"] = str(update_data["email"])

        return self.repo.update(member, **update_data)

    def list(
        self,
        skip: int = 0,
        limit: int = 20,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Tuple[int, List[Member]]:
        return self.repo.list(skip=skip, limit=limit, name=name, email=email)
