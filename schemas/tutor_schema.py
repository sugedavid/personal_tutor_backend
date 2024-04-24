from typing import Dict, List, Optional

from pydantic import BaseModel
from pydantic_extra_types.isbn import *


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
    tools: List[AssistantTools]
    metadata: Dict[str, Any]
    
class AssistantResponse(BaseModel):
    id: str
    assistant: Assistant
    user_id: str