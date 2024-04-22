from enum import Enum

from pydantic import BaseModel
from pydantic_extra_types.isbn import *


class CreditTypeEnum(str, Enum):
    topUp = 'Top up'
    createTutor = 'Create Tutor'
    updateTutor = 'Update Tutor'
    createModule = 'Create Module'
    updateModule = 'Update Module'
    personalTutor = 'Chat'
class CreditRequest(BaseModel):
    amount: float

class CreditResponse(BaseModel):
    id: str
    amount: float
    currency: str
    type: CreditTypeEnum
    created_at: int