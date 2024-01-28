from logging import getLogger
from typing import List

from fastapi import APIRouter, Query
from fastapi import HTTPException
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from database.db import get_db
from database.models import User
from database.schemas import CategoryCreate, ShowCategory, CreatePost, ShowPost, ShowPostDetail, DeletePostResponse
from crud.post_crud import _create_new_category, _create_new_post, _get_list_posts, _get_post, _delete_post
from crud.user_crud import get_current_user_from_token
from api.user_router import _check_admin_role

from utils import PostFilter

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
        raise HTTPException(status_code=503, detail=f'Database error: {err}')
    

@router.post('/create_post', response_model=ShowPost)
async def create_post(body: CreatePost, 
                      db: AsyncSession = Depends(get_db), 
                      author: User = Depends(get_current_user_from_token)):
    try:
        return await _create_new_post(body, db, author)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f'Database error: {err}')
    

@router.get('/', response_model=List[ShowPostDetail])
async def get_posts(
    db: AsyncSession = Depends(get_db),
    page: int = Query(0, ge=0),
    size: int = Query(10, le=100),
    filter_params: PostFilter = Depends(PostFilter),
    sort_by: str = 'id',
    sort_desc: bool = False
):
    try:
        return await _get_list_posts(db=db, page=page, size=size, post_filter=filter_params, sort_by=sort_by, sort_desc=sort_desc)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f'Database error: {err}')
      

@router.get('/{post_id}', response_model=ShowPostDetail)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    try:
        post = await _get_post(post_id, db)
        if not post:
            raise HTTPException(
                status_code=404,
                detail=f'Post number {post_id} does not exist.')
        return post.as_show_model()
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f'Database error: {err}')


@router.delete('/delete_post', response_model=DeletePostResponse)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    post = await _get_post(post_id, db)
    if not post:
        raise HTTPException(
            status_code=404,
            detail=f'Post number {post_id} does not exist.') 

    try:
        if current_user.id == post.user_id:
            await _delete_post(post_id, db)
        else:
            _check_admin_role(current_user)
            await _delete_post(post_id, db)
        return DeletePostResponse(deleted_post_id=post_id)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f'Database error: {err}')