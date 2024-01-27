from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from typing import List

from database.models import Category, Post, User
from database.schemas import CategoryCreate, ShowCategory, CreatePost, ShowPost, ShowPostList
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
    

async def _create_new_post(body: CreatePost, db: AsyncSession, author: User) -> ShowPost:
    async with db.begin():
        db_post = Post(
            title=body.title,
            content=body.content,
            price=Decimal(body.price),
            category_id=body.category_id,
            author=author,
        )
        db.add(db_post)
        await db.flush()
        return ShowPost(
            id=db_post.id,
            title=db_post.title,
            content=db_post.content,
            price=Decimal(body.price),
            user_id=db_post.user_id,
            category_id=db_post.category_id
        )


async def _get_list_posts(db: AsyncSession) -> List[ShowPostList]:
    result = await db.execute(select(Post).options(joinedload(Post.author), joinedload(Post.category)))
    posts = result.scalars().all()
    return [post.as_show_model() for post in posts]