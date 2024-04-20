import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Security
from fastapi.security import OAuth2PasswordBearer
from firebase_admin import firestore
from openai import OpenAI

from schemas.credit_schema import CreditTypeEnum
from schemas.tutor_schema import (AssistantResponse, CreateAssistantRequest,
                                  CreateAssistantResponse)
from utils import update_credit, validate_firebase_token

router = APIRouter()

openai_client = OpenAI(api_key=os.getenv("PERSONAL_TUTOR_OPENAI_API_KEY"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    return firestore.client()

# create tutor api
@router.post("/tutors", response_model=CreateAssistantResponse)
async def create_tutor(user_data: CreateAssistantRequest, db: firestore.client = Depends(get_db), token: str = Security(oauth2_scheme)):
    try:
        await update_credit(token=token, amount=0.05, type=CreditTypeEnum.createTutor, db=db)

        # user info
        userFromToken = await validate_firebase_token(token)
        user_id = userFromToken.get("uid")

        # create assistant
        assistant = openai_client.beta.assistants.create(
            name=user_data.name,
            instructions=user_data.instructions,
            tools=user_data.tools,
            model="gpt-3.5-turbo-1106"
        )

        # save to db
        assistants_doc_ref = db.collection("tutors").document(assistant.id)
        assistants_doc_ref.set(
            { 
                "id": assistant.id,
                "assistant": assistant.model_dump(),
                "user_id": user_id
            }
        )
        
        return CreateAssistantResponse(assistant_id=assistant.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# update tutor api
@router.put("/tutors/{assistant_id}")
async def update_tutor(assistant_id: str, user_data: CreateAssistantRequest, db: firestore.client = Depends(get_db), token: str = Security(oauth2_scheme)):
    try:
        await update_credit(token=token, amount=0.01, type=CreditTypeEnum.updateTutor, db=db)
        
        # update assistant
        assistant = openai_client.beta.assistants.update(
            assistant_id=assistant_id,
            name=user_data.name,
            instructions=user_data.instructions,
            tools=user_data.tools,
        )

        # update db
        doc_ref = db.collection("tutors").document(assistant_id)
        doc_ref.update(
             { 
                "assistant": assistant.model_dump(),
            }
        )
        
        return CreateAssistantResponse(assistant_id=assistant.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# delete tutor api
@router.delete("/tutors/{assistant_id}")
async def delete_tutor(assistant_id: str, db: firestore.client = Depends(get_db), token: str = Security(oauth2_scheme)):
    try:
        await validate_firebase_token(token)
        # delete assistant
        openai_client.beta.assistants.delete(
            assistant_id=assistant_id
        )
         # delete doc from db
        db.collection("tutors").document(assistant_id).delete()
        
        return {"message": "Personal tutor deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# list tutors api
@router.get("/tutors", response_model=List[AssistantResponse])
async def list_tutors(order_by: str = Query("desc"), limit: int = Query(20), db: firestore.client = Depends(get_db), token: str = Security(oauth2_scheme)):
    try:
        # user info
        userFromToken = await validate_firebase_token(token)
        user_id = userFromToken.get("uid")
      
        # fetch all documents
        doc_ref = db.collection("tutors").where("user_id", "==", user_id).order_by(order_by).limit(limit).stream()
        
        # parse documents
        tutors_data = []
        for doc in doc_ref:
            tutor_data_data = doc.to_dict()
            tutor_data_data["id"] = doc.id
            tutors_data.append(AssistantResponse(**tutor_data_data))
        
        return tutors_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))