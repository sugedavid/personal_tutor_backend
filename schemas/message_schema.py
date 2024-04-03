from typing import Dict, List, Optional, Union

from pydantic import BaseModel
from pydantic_extra_types.isbn import *


class MessageRequest(BaseModel):
    assistant_id: str
    thread_id: str
    content: str
    user_id: str
    instructions: Optional[str]

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