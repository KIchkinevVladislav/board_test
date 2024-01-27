from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Category
from database.schemas import CategoryCreate, ShowCategory
from database.db import get_db


async def _create_new_category(body: CategoryCreate, db: AsyncSession) -> ShowCategory:
    async with db.begin():
        db_category = Category(
            title=body.title,
            description=body.description,
        )
        db.add(db_category)
        await db.flush()
        return ShowCategory(
            id=db_category.id,
            title=db_category.title,
            description=db_category.description,
        )