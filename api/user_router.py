from logging import getLogger
from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter
from fastapi import HTTPException, status
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm



from database.db import get_db
from database.schemas import ShowUser, UserCreate, Token, UpdatedUserResponse
from crud.user_crud import (_create_new_user, authenticate_user, create_access_token, 
                            get_current_user_from_token, _get_user_by_id, _update_user)

from crud.user_crud import ACCESS_TOKEN_EXPIRE_MINUTES

from database.models import User

logger = getLogger(__name__)

router = APIRouter()


@router.post('/sign-up', response_model=ShowUser)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    try:
        return await _create_new_user(body, db)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")



@router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password'
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.email, 'other_custom_data': [1, 2, 3, 4]},
        expires_delta=access_token_expires,
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


# @router.get("/test_auth_endpoint")
# async def sample_endpoint_under_jwt(
#     current_user: User = Depends(get_current_user_from_token),
# ):
#     return {"Success": True, "current_user": current_user}


def _check_admin_role(current_user):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403, detail='Only an administrator can do this.'
        )
    

def _check_not_yourself(current_user, user_id):
    if current_user.id == user_id:
        raise HTTPException(
            status_code=400, detail='Cannot manage privileges of itself.'
        )


def _check_user_for_promotion_or_revoke(user, promotion=True):
    if user is None:
        raise HTTPException(
            status_code=404, detail=f'User not found.'
        )
    if promotion:    
        if user.is_admin:
            raise HTTPException(
                status_code=409,
                detail=f'User with id {user.id} already promoted to admin',
            )
    if not user.is_admin:
        raise HTTPException(
            status_code=409, 
            detail=f"User with id {user.id} has no admin privileges."
        )
    


@router.patch('/admin_privilege', response_model=UpdatedUserResponse)
async def grant_admin_privilege(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    _check_admin_role(current_user)

    _check_not_yourself(current_user, user_id)

    user_for_promotion = await _get_user_by_id(user_id, db)

    _check_user_for_promotion_or_revoke(user_for_promotion, True)

    updated_user_params = {
        'roles': user_for_promotion.adding_admin_role()
    }
    try:
        updated_user_id = await _update_user(
            updated_user_params=updated_user_params, db=db, user_id=user_id
        )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f'Database error: {err}')
    return UpdatedUserResponse(updated_user_id=updated_user_id)


@router.delete('/admin_privilege', response_model=UpdatedUserResponse)
async def revoke_admin_privilege(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    _check_admin_role(current_user)

    _check_not_yourself(current_user, user_id)

    user_for_revoke_admin_privileges = await _get_user_by_id(user_id, db)

    _check_user_for_promotion_or_revoke(user_for_revoke_admin_privileges, False)

    updated_user_params = {
        "roles": user_for_revoke_admin_privileges.remove_admin_role()
    }
    try:
        updated_user_id = await _update_user(
            updated_user_params=updated_user_params, db=db, user_id=user_id
        )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdatedUserResponse(updated_user_id=updated_user_id)