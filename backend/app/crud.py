from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models import User, UserCreate


async def create_user(*, session: AsyncSession, user_create: UserCreate) -> User:
    db_obj = User.model_validate(user_create, update={"hashed_password": get_password_hash(user_create.password)})
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj


async def get_user_by_email(*, session: AsyncSession, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    result = await session.exec(statement)
    return result.first()


async def get_user_by_oauth_subject(*, session: AsyncSession, oauth_subject: str) -> User | None:
    """Get user by OAuth subject (OAuth provider sub claim)."""
    statement = select(User).where(User.oauth_subject == oauth_subject)
    result = await session.exec(statement)
    return result.first()


async def authenticate(*, session: AsyncSession, email: str, password: str) -> User | None:
    db_user = await get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    # OAuth users don't have passwords
    if not db_user.hashed_password:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user
