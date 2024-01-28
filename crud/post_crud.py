from typing import List
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.orm import joinedload, selectinload
from fastapi_filter import FilterDepends

from utils import PostFilter

from database.models import Category, Post, User
from database.schemas import CategoryCreate, ShowCategory, CreatePost, ShowPost, ShowPostDetail
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
    

async def _get_list_posts(db: AsyncSession, page: int, size: int, post_filter: PostFilter = FilterDepends(PostFilter)) -> List[ShowPostDetail]:
    async with db.begin():
        query = select(Post).offset(page*size).limit(size).options(
            selectinload(Post.author),
            selectinload(Post.category)
        )

        query = post_filter.filter(query)
        result = await db.execute(query)
        posts = result.scalars().all()
        return [
            ShowPostDetail(
                id=post.id,
                title=post.title,
                content=post.content,
                price=post.price,
                user_email=post.author.email,
                category_name=post.category.title
            )
            for post in posts
        ]


async def _get_post(post_id: int, db: AsyncSession) -> Post:
    async with db.begin():
        post = await db.execute(
            select(Post).where(Post.id == post_id).options(
                joinedload(Post.author),
                joinedload(Post.category)
            )
        )
        return post.scalars().first()
        
    
async def _delete_post(post_id: int, db: AsyncSession) -> int:
    exists_statement = delete(Post).where(
        (Post.id == post_id)
    )
    await db.execute(exists_statement)
    await db.commit()

    return post_id