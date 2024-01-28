from decimal import Decimal
from typing import Optional
from database.models import Post

from passlib.context import CryptContext
from fastapi_filter import FilterDepends
from fastapi_filter.contrib.sqlalchemy import Filter

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class Hasher:
    """
    Password hashing and verification.
    """
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
    


class PostFilter(Filter):
    """
    Custom filter for displaying posts.
    """
    title__ilike: Optional[str] = None
    price__gte: Optional[Decimal] = None
    price__lte: Optional[Decimal] = None
    category_id: Optional[int] = None

    class Constants(Filter.Constants):
        model = Post

    class Config:
        allow_population_by_field_name = True