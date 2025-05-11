# Crud юзеров
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared import logger_setup
from src.shared.models import User
from src.user_service.auth_functions import get_password_hash, verify_password
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
    logger.info(f"User create data {db_user}")
    async with db.begin():
        db.add(db_user)
    await db.refresh(db_user)
    logger.info(f"User created data {db_user}")
    return db_user


async def update_user(db: AsyncSession, user_name: str, user: UserUpdate):
    async with db.begin():
        db_user = await db.execute(select(User).filter(User.username == user_name))
        db_user = db_user.scalar()
        if db_user is None:
            logger.error(f"User {user_name} not found.")
            return None
        logger.info(f"Found old user {db_user.to_dict()}")
        update_data = user.model_dump(exclude_unset=True)
        logger.info(f"Updating user {update_data}")
        if "password" in update_data:
            password = update_data.pop("password")
            update_data["hashed_password"] = get_password_hash(password)
            logger.info(f"Updated password {update_data['hashed_password']} {password}")
        for key, value in update_data.items():
            setattr(db_user, key, value)
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user: User):
    async with db.begin():
        result = await db.execute(select(User).filter(User.username == user.username))
        db_user = result.scalar_one_or_none()
        if not db_user:
            logger.warning(f"User {user.username} not found.")
            return None
        logger.info(f"Deleted user {db_user.to_dict()}")
        await db.delete(db_user)
    return db_user


async def get_user_by_email(db: AsyncSession, email: str):
    async with db.begin():
        db_user = await db.execute(select(User).filter(User.email == email))
        db_user = db_user.scalar_one_or_none()
        logger.info(f"Found user {db_user}")
        return db_user


async def get_user_by_username(db: AsyncSession, username: str):
    async with db.begin():
        db_user = await db.execute(select(User).filter(User.username == username))
        db_user = db_user.scalar_one_or_none()
        logger.info(f"Found user {db_user}")
        return db_user


async def get_users(db: AsyncSession):
    async with db as session:
        result = await session.execute(select(User))
        result = result.scalars().all()
        logger.info(f"Found users {result}")
        return result


async def authenticate_user(db: AsyncSession, identifier: str, password: str):
    user = await get_user_by_email(db, identifier) or await get_user_by_username(db, identifier)
    if not user:
        logger.error(f"User {identifier} not found.")
        return None
    if not verify_password(password, user.hashed_password):
        logger.error(f"User {identifier} dont have correct password.")
        return None
    logger.info(f"Authenticated user {user.to_dict()}")
    return user
