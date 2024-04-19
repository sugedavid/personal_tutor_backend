from pydantic import BaseModel
from pydantic_extra_types.isbn import *

class UserRegistrationRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class UserResponse(BaseModel):
    user_id: str
    first_name: str
    last_name: str
    display_name: str
    email: str
    credits: float
    currency: str