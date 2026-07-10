import uuid
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.logging import get_logger
from app.models.member import Member
from app.repositories.member_repository import MemberRepository
from app.schemas.member import MemberCreate, MemberUpdate

logger = get_logger(__name__)


class MemberService:
    def __init__(self, db: Session):
        self.repo = MemberRepository(db)

    def create(self, payload: MemberCreate) -> Member:
        logger.info(f"Creating member with email: {payload.email}")
        existing = self.repo.get_by_email(str(payload.email))
        if existing:
            logger.warning(f"Member with email '{payload.email}' already exists")
            raise ConflictError(f"A member with email '{payload.email}' already exists.")
        member = self.repo.create(
            name=payload.name,
            email=str(payload.email),
            phone=payload.phone,
            address=payload.address,
        )
        logger.info(f"Successfully created member with ID: {member.id}")
        return member

    def get(self, member_id: uuid.UUID) -> Member:
        logger.info(f"Fetching member with ID: {member_id}")
        member = self.repo.get_by_id(member_id)
        if not member:
            logger.warning(f"Member not found with ID: {member_id}")
            raise NotFoundError("Member", str(member_id))
        logger.info(f"Successfully fetched member with ID: {member_id}")
        return member

    def update(self, member_id: uuid.UUID, payload: MemberUpdate) -> Member:
        logger.info(f"Updating member with ID: {member_id}")
        member = self.get(member_id)

        if payload.email and str(payload.email) != member.email:
            existing = self.repo.get_by_email(str(payload.email))
            if existing:
                logger.warning(f"Member with email '{payload.email}' already exists")
                raise ConflictError(f"A member with email '{payload.email}' already exists.")

        update_data = payload.model_dump(exclude_unset=True, exclude_none=True)
        if "email" in update_data:
            update_data["email"] = str(update_data["email"])

        updated_member = self.repo.update(member, **update_data)
        logger.info(f"Successfully updated member with ID: {member_id}")
        return updated_member

    def list(
        self,
        skip: int = 0,
        limit: int = 20,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Tuple[int, List[Member]]:
        logger.info(f"Listing members with filters - skip: {skip}, limit: {limit}, name: {name}, email: {email}")
        total, items = self.repo.list(skip=skip, limit=limit, name=name, email=email)
        logger.info(f"Found {total} members, returning {len(items)} items")
        return total, items
