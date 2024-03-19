from fastapi import APIRouter, HTTPException, Query, Depends
from openai import OpenAI
from utils import validate_firebase_token
import os

from schemas_t.tutors_schema import (AssistantResponse, CreateAssistantRequest, CreateAssistantResponse)

router = APIRouter()

openai_client = OpenAI(api_key=os.getenv("PERSONAL_TUTOR_OPENAI_API_KEY"))

# create tutor api
@router.post("/tutors", response_model=CreateAssistantResponse)
async def create_tutor(user_data: CreateAssistantRequest, token: str = Depends(validate_firebase_token)):
    try:
        # create assistant
        assistant = openai_client.beta.assistants.create(
            name=user_data.name,
            instructions=user_data.instructions,
            tools=user_data.tools,
            model="gpt-3.5-turbo-1106"
        )
        
        return CreateAssistantResponse(assistant_id=assistant.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# update tutor api
@router.put("/tutors/{assistant_id}")
async def update_tutor(assistant_id: str, user_data: CreateAssistantRequest, token: str = Depends(validate_firebase_token)):
    try:
        # update assistant
        assistant = openai_client.beta.assistants.update(
            assistant_id=assistant_id,
            name=user_data.name,
            instructions=user_data.instructions,
            tools=user_data.tools,
        )
        
        return CreateAssistantResponse(assistant_id=assistant.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# delete tutor api
@router.delete("/tutors/{assistant_id}")
async def delete_tutor(assistant_id: str, token: str = Depends(validate_firebase_token)):
    try:
        # delete assistant
        assistant = openai_client.beta.assistants.delete(
            assistant_id=assistant_id
        )
        
        return CreateAssistantResponse(assistant_id=assistant.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# fetch tutors api
@router.get("/tutors", response_model=AssistantResponse)
async def list_tutors(order: str = Query("desc"), limit: int = Query(20), token: str = Depends(validate_firebase_token)):
    try:
        my_assistants = openai_client.beta.assistants.list(
            order=order,
            limit=str(limit),
        )

        # convert assistant instances to dictionaries
        assistant_data = [assistant.model_dump() for assistant in my_assistants.data]
        
        return AssistantResponse(object=my_assistants.object, data=assistant_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))