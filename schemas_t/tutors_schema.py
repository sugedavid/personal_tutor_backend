from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, RootModel, field_validator, validator
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
    tools: List[str]
    file_ids: List[str]
    metadata: Dict[str, Any]

class AssistantResponse(BaseModel):
    object: str
    data: List[Assistant]