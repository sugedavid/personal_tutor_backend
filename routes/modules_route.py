import os
import time
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Security
from fastapi.security import OAuth2PasswordBearer
from firebase_admin import firestore
from openai import OpenAI

from schemas.credit_schema import CreditTypeEnum
from schemas.module_schema import ModuleRequest, ModuleResponse
from utils import update_credit, validate_firebase_token

router = APIRouter()
openai_client = OpenAI(api_key=os.getenv("PERSONAL_TUTOR_OPENAI_API_KEY"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    return firestore.client()

# create module api
@router.post("/modules", response_model=ModuleResponse)
async def create_module( user_data: ModuleRequest, db: firestore.client = Depends(get_db), token: str = Security(oauth2_scheme)):
    try:
        await update_credit(token=token, amount=0.05, type=CreditTypeEnum.createModule, db=db)
        # get assistant info
        assistant = openai_client.beta.assistants.retrieve(user_data.assistant_id)

        # user info
        userFromToken = await validate_firebase_token(token)
        user_id = userFromToken.get("uid")

        # create a new thread
        thread = openai_client.beta.threads.create()
        thread_id = thread.id

        current_time = int(time.time())

        # save to db
        module_doc_ref = db.collection("modules").document()
        module_doc_ref.set(
            { 
                "id": module_doc_ref.id,
                "name": user_data.name,
                "assistant": assistant.model_dump(),
                "thread_id": thread_id,
                "created_at": current_time,
                "user_id": user_id
            }
        )
        
        return ModuleResponse(id=module_doc_ref.id, name=user_data.name, assistant=assistant, thread_id=thread_id, created_at=current_time, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# update module api
@router.put("/modules/{id}")
async def update_module(id: str, user_data: ModuleRequest, db: firestore.client = Depends(get_db), token: str = Security(oauth2_scheme)):
    try:
        await update_credit(token=token, amount=0.01, type=CreditTypeEnum.updateModule, db=db)
        # update db
        doc_ref = db.collection("modules").document(id)

        update_data = {}
        if user_data.name:
            update_data["name"] = user_data.name
        if user_data.assistant_id:
            # get assistant info
            assistant = openai_client.beta.assistants.retrieve(user_data.assistant_id)
            update_data["assistant"] = assistant.model_dump()

        doc_ref.update(update_data)
        
        return {"message": "Module updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# delete module api
@router.delete("/modules/{id}")
async def delete_module(id: str, db: firestore.client = Depends(get_db), token: str = Security(oauth2_scheme)):
    try:
        await validate_firebase_token(token)
        # delete doc from db
        db.collection("modules").document(id).delete()
        
        return {"message": "Module deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# list modules api
@router.get("/modules", response_model=List[ModuleResponse])
async def list_modules(order_by: str = Query("name"), limit: int = Query(20), db: firestore.client = Depends(get_db), token: str = Security(oauth2_scheme)):
    try:
        # user info
        userFromToken = await validate_firebase_token(token)
        user_id = userFromToken.get("uid")

        # fetch all documents
        modules_ref = db.collection("modules").where("user_id", "==", user_id).order_by(order_by).limit(limit).stream()
        
        # parse documents
        modules_data = []
        for doc in modules_ref:
            module_data = doc.to_dict()
            module_data["id"] = doc.id
            modules_data.append(ModuleResponse(**module_data))
        
        return modules_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))