from pydantic import BaseModel,RootModel,validator,Field,field_validator
from pydantic_extra_types.isbn import *
from typing import List
from uuid import UUID, uuid4
from enum import Enum

class UserRegistrationRequest(BaseModel):
    email: str
    password: str

class UserRegistrationResponse(BaseModel):
    userId: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserLoginResponse(BaseModel):
    idToken: str
    refreshToken: str
    authTime: str
    userId: str
    emailVerified: bool