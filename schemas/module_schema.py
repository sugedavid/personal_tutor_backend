from pydantic import BaseModel
from pydantic_extra_types.isbn import *


class ModuleRequest(BaseModel):
    name: str
    assistant_id: str

class ModuleResponse(BaseModel):
    id: str
    name: str
    assistant: object
    thread_id:  str
    created_at: int
    user_id: str