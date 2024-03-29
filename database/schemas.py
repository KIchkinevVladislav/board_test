import re
import uuid
from decimal import Decimal
from typing import List

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, validator


LETTER_MATCH_PATTERN = re.compile(r'^[а-яА-Яa-zA-Z\-]+$')

class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str

    @validator('name')
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail='Name should contains only letters'
            )
        return value

    @validator('surname')
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail='Surname should contains only letters'
            )
        return value


class TunedModel(BaseModel):
    class Config:
        """Tells pydantic to convert even non dict obj to json"""

        from_attributes = True


class ShowUser(TunedModel):
    user_id: uuid.UUID
    name: str
    surname: str
    email: EmailStr
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class UpdatedUserResponse(BaseModel):
    updated_user_id: uuid.UUID


class CategoryCreate(BaseModel):
    title: str
    description: str


class ShowCategory(TunedModel):
    id: int
    title: str
    description: str


class CreatePost(BaseModel):
    title: str
    content: str
    category_id: int
    price: Decimal


class ShowPost(TunedModel):
    id: int
    title: str
    content: str
    price: Decimal

    user_id: uuid.UUID
    category_id: int


class ShowPostDetail(TunedModel):
    id: int
    title: str
    content: str
    price: Decimal
    user_email: str
    category_name: str


class DeletePostResponse(BaseModel):
    deleted_post_id: int