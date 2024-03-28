import os

from fastapi import APIRouter, Depends, HTTPException, Query
from firebase_admin import firestore
from openai import OpenAI

from schemas_t.message_schema import MessageRequest, MessageResponse
from utils import validate_firebase_token

router = APIRouter()
openai_client = OpenAI(api_key=os.getenv("PERSONAL_TUTOR_OPENAI_API_KEY"))

def get_db():
    return firestore.client()

# create message api
@router.post("/messages", response_model=MessageResponse)
async def create_message(user_data: MessageRequest):
    try:
        thread_id = user_data.thread_id
        instructions = user_data.instructions if user_data.instructions else "Please address the user as {user_data.firstName}. The user is a {user_data.userType}"

        # create message
        openai_client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_data.content
        )

        # run assistant
        openai_client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=user_data.assistant_id,
            instructions=instructions,
        )

        # assistant response
        messages = openai_client.beta.threads.messages.list(
            thread_id=thread_id
        )

        message_data = [message.model_dump() for message in messages.data]

        return MessageResponse(object=messages.object, data=message_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# fetch messages api
@router.get("/messages", response_model=MessageResponse)
async def list_messages(thread_id: str, token: str = Depends(validate_firebase_token)):
    try:
        messages = openai_client.beta.threads.messages.list(
            thread_id=thread_id
        )

        # convert message instances to dictionaries
        message_data = [message.model_dump() for message in messages.data]

        return MessageResponse(object=messages.object, data=message_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))