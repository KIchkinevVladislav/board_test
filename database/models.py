import uuid
from enum import Enum
from sqlalchemy import (
    Boolean,
    Column,
    String,
    Integer,
    Text,
    ForeignKey,
    )
from sqlalchemy.dialects.postgresql import (
    ARRAY,
    UUID
    )
from sqlalchemy.orm import relationship

from .db import Base

"""
Block with database models.
"""

class Role(str, Enum):
    """
    We describe user roles in the system
    """
    ROLE_USER = 'ROLE_USER'
    ROLE_ADMIN = 'ROLE_ADMIN'


class User(Base):
    """
    Define the user model.
    """
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean(), default=True)
    hashed_password = Column(String, nullable=False)
    roles = Column(ARRAY(String), nullable=False)

    posts = relationship(
        'Post',
        back_populates='author',
        cascade='all, delete-orphan',
    )

    @property
    def is_admin(self):
        return Role.ROLE_ADMIN in self.roles
    

    def adding_admin_role(self):
        if not self.is_admin:
            return {*self.roles, Role.ROLE_ADMIN}
        
    
    def remove_admin_role(self):
        if self.is_admin:
            return {role for role in self.roles if role != Role.ROLE_ADMIN}


class Post(Base):
    """
    Define the post model.
    """    
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128))
    content = Column(Text)

    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('users.id', ondelete='CASCADE'), 
            nullable=False
    )    
    category_id = Column(
        Integer,
        ForeignKey('categories.id'),
        nullable=False,
    )

    author = relationship('User', back_populates='posts')
    category = relationship('Category', back_populates='posts')


class Category(Base):
    """
    Define the сategory model.

    """ 
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(32))
    description = Column(Text)

    posts= relationship('Post', back_populates='category')