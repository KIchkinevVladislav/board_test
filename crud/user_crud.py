
from typing import Optional
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from jose import jwt, JWTError

from envparse import Env

from database.models import Role, User
from database.schemas import UserCreate, ShowUser
from database.dals import UserDAL
from database.db import get_db
from hashing import Hasher
"""
Block for working with the user model, 
registration and authorization.
"""
env = Env()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")


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
    

async def _get_user_by_email_for_auth(
        email: str, db: AsyncSession
):
    async with db.begin():
        user_dal = UserDAL(db)
        return await user_dal.get_user_by_email(
            email=email,
        )
    

async def authenticate_user(
        email: str, password: str, db: AsyncSession
):
    user = await _get_user_by_email_for_auth(email=email, db=db)
    if user is None:
        return
    if not Hasher.verify_password(password, user.hashed_password):
        return
    return user


# variables to configure JWT
SECRET_KEY = env.str('SECRET_KEY', default='secret_key')
ALGORITHM = env.str('ALGORITHM', default='HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = env.int('ACCESS_TOKEN_EXPIRE_MINUTES', default=30)


async def get_current_user_from_token(
        token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
    )
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY,
            algorithms = [ALGORITHM],
        )
        email: str = payload.get('sub')
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await _get_user_by_email_for_auth(email=email, db=db)
    if user is None:
        raise credentials_exception
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded_jwt


async def _get_user_by_id(user_id, db: AsyncSession):
    async with db.begin():
        user_dal = UserDAL(db)
        user = await user_dal.get_user_by_id(
            user_id=user_id,
        )
        if user is not None:
            return user
        

async def _update_user(
    updated_user_params: dict, user_id: UUID, db: AsyncSession
):
    async with db.begin():
        user_dal = UserDAL(db)
        updated_user_id = await user_dal.update_user(
            user_id=user_id, **updated_user_params
        )
        return updated_user_id