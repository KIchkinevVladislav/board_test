from logging import getLogger
from datetime import timedelta

from fastapi import APIRouter
from fastapi import HTTPException, status
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm



from database.db import get_db
from database.schemas import ShowUser, UserCreate, Token
from crud.user_crud import _create_new_user, authenticate_user, create_access_token, get_current_user_from_token
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