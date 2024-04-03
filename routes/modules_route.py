import os
import time
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from firebase_admin import firestore
from openai import OpenAI

from schemas.module_schema import ModuleRequest, ModuleResponse
from utils import validate_firebase_token

router = APIRouter()
openai_client = OpenAI(api_key=os.getenv("PERSONAL_TUTOR_OPENAI_API_KEY"))

def get_db():
    return firestore.client()

# create module api
@router.post("/modules", response_model=ModuleResponse)
async def create_module( user_data: ModuleRequest, db: firestore.client = Depends(get_db), token: str = Depends(validate_firebase_token)):
    try:
        # get assistant info
        assistant = openai_client.beta.assistants.retrieve(user_data.assistant_id)

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
                "created_at": current_time
            }
        )
        
        return ModuleResponse(id=module_doc_ref.id, name=user_data.name, assistant=assistant, thread_id=thread_id, created_at=current_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# update module api
@router.put("/modules/{id}")
async def update_module(id: str, user_data: ModuleRequest, db: firestore.client = Depends(get_db), token: str = Depends(validate_firebase_token)):
    try:
        # update db
        doc_ref = db.collection("modules").document(id)

        update_data = {}
        if user_data.name:
            update_data["name"] = user_data.name
        if user_data.assistant_id:
            update_data["assistant_id"] = user_data.assistant_id

        doc_ref.update(update_data)
        
        return {"message": "Module updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# delete module api
@router.delete("/modules/{id}")
async def delete_module(id: str, db: firestore.client = Depends(get_db), token: str = Depends(validate_firebase_token)):
    try:
        # delete doc from db
        db.collection("modules").document(id).delete()
        
        return {"message": "Module deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# list modules api
@router.get("/modules", response_model=List[ModuleResponse])
async def list_modules(order: str = Query("name"), limit: int = Query(20), db: firestore.client = Depends(get_db), token: str = Depends(validate_firebase_token)):
    try:
        # fetch all documents
        modules_ref = db.collection("modules").stream()
        
        # parse documents
        modules_data = []
        for doc in modules_ref:
            module_data = doc.to_dict()
            module_data["id"] = doc.id
            modules_data.append(ModuleResponse(**module_data))
        
        return modules_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))