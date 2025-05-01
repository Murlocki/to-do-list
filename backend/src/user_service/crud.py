# Crud юзеров
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared import logger_setup
from src.user_service.auth_functions import get_password_hash, verify_password
from src.user_service.models import User
from src.user_service.schemas import UserCreate, UserUpdate

logger = logger_setup.setup_logger(__name__)


# CRUD операции с пользователями
async def create_user(db: AsyncSession, user: UserCreate):
    user_password_hash = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=str(user.email),
        hashed_password=user_password_hash,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=False,
    )
    async with db.begin():
        db.add(db_user)
    await db.refresh(db_user)
    return db_user


async def update_user(db: AsyncSession, user_name: str, user: UserUpdate):
    async with db.begin():
        db_user = await db.execute(select(User).filter(User.username == user_name))
        db_user = db_user.scalar()
        if db_user is None:
            logger.warning(f"User {user_name} not found.")
            return None
        logger.info(f"Found old user {db_user.to_dict()}")
        update_data = user.model_dump(exclude_unset=True)
        logger.info(f"Updating user {update_data}")
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
            logger.info(f"Updated password {update_data['hashed_password']}")
        for key, value in update_data.items():
            setattr(db_user, key, value)
    await db.refresh(db_user)
    return db_user


def delete_user(db: AsyncSession, user_name: str):
    db_user = db.query(User).filter(User.username == user_name).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user


async def get_user_by_email(db: AsyncSession, email: str):
    async with db.begin():
        db_user = await db.execute(select(User).filter(User.email == email))
        return db_user.scalar()


async def get_user_by_username(db: AsyncSession, username: str):
    async with db.begin():
        db_user = await db.execute(select(User).filter(User.username == username))
        return db_user.scalar()


async def get_users(db: AsyncSession):
    async with db as session:
        result = await session.execute(select(User))
        return result.scalars().all()


async def authenticate_user(db: AsyncSession, identifier: str, password: str):
    user = await get_user_by_email(db, identifier) or await get_user_by_username(db, identifier)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
