
from sqlalchemy.ext.asyncio import AsyncSession

from hashing import Hasher

from database.models import Role, User
from database.schemas import UserCreate, ShowUser
from database.dals import UserDAL



async def _create_new_user(body: UserCreate, db: AsyncSession) -> ShowUser:
    async with db.begin():
        user_dal = UserDAL(db)
        user = await user_dal.create_user(
            name=body.name,
            surname=body.surname,
            email=body.email,
            hashed_password=Hasher.get_password_hash(body.password),
            roles=[
                Role.ROLE_USER,
            ],
        )
        return ShowUser(
            user_id=user.id,
            name=user.name,
            surname=user.surname,
            email=user.email,
            is_active=user.is_active,
        )