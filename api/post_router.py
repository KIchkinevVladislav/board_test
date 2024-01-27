from logging import getLogger
from typing import List


from fastapi import APIRouter
from fastapi import HTTPException, status
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from database.db import get_db
from database.models import User, Post
from database.schemas import CategoryCreate, ShowCategory, CreatePost, ShowPost, ShowPostList
from crud.post_crud import _create_new_category, _create_new_post, _get_list_posts
from crud.user_crud import get_current_user_from_token
from api.user_router import _check_admin_role


logger = getLogger(__name__)

router = APIRouter()

@router.post('/create_category', response_model=ShowCategory)
async def create_category(body: CategoryCreate, 
                          db: AsyncSession = Depends(get_db), 
                          current_user: User = Depends(get_current_user_from_token)):
    # Only an administrator can create categories
    _check_admin_role(current_user)
    try:
        return await _create_new_category(body, db)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    


@router.post('/create_post', response_model=ShowPost)
async def create_post(body: CreatePost, 
                      db: AsyncSession = Depends(get_db), 
                      author: User = Depends(get_current_user_from_token)):
    try:
        return await _create_new_post(body, db, author)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    

@router.get('/', response_model=List[ShowPostList])
async def get_posts(db: AsyncSession = Depends(get_db)):
    try:
        return await _get_list_posts(db)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")