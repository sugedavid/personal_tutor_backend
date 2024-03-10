from pydantic import BaseModel,RootModel,validator,Field,field_validator
from pydantic_extra_types.isbn import *
from typing import List, Optional, Dict, Union
from uuid import UUID, uuid4
from enum import Enum

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

# opneai schemas
class AssistantTools(BaseModel):
    type: str
class CreateAssistantRequest(BaseModel):
    name: str
    instructions: str
    tools: Optional[List[AssistantTools]]

class CreateAssistantResponse(BaseModel):
    assistant_id: str

class Assistant(BaseModel):
    id: str
    object: str
    created_at: int
    name: str
    description: Any  # can be either a string or null
    model: str
    instructions: str
    tools: List[str]
    file_ids: List[str]
    metadata: Dict[str, Any]

class AssistantResponse(BaseModel):
    object: str
    data: List[Assistant]

class MessageRequest(BaseModel):
    assistant_id: str
    thread_id: str
    content: str
    instructions: Optional[str]
    user_id: str
    firstName: str
    userType: str

class TextContent(BaseModel):
    type: str
    text: Dict[str, Union[str, List[str]]]

class Message(BaseModel):
    created_at: int
    id: str
    object: str
    thread_id: str
    role: str
    content: List[TextContent]

class MessageResponse(BaseModel):
    object: str
    data: List[Message]

class Thread(BaseModel):
    thread_id: str
    assistant_id: str
    user_id: str
    created_at: int

class ThreadsResponse(BaseModel):
    data: List[Thread]