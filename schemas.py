from pydantic import BaseModel
from pydantic_extra_types.isbn import *


# firebase schemas
class UserRegistrationRequest(BaseModel):
    email: str
    password: str
    type: str

class UserRegistrationResponse(BaseModel):
    user_id: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserLoginResponse(BaseModel):
    id_token: str
    refresh_token: str
    auth_time: str
    user_id: str
    email_verified: bool