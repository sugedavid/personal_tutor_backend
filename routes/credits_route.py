import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Security
from fastapi.security import OAuth2PasswordBearer
from fastapi_limiter.depends import RateLimiter
from firebase_admin import firestore
from openai import OpenAI

from schemas.credit_schema import CreditRequest, CreditResponse, CreditTypeEnum
from utils import update_credit, validate_firebase_token

router = APIRouter()
openai_client = OpenAI(api_key=os.getenv("PERSONAL_TUTOR_OPENAI_API_KEY"))


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    return firestore.client()
    
# create credit api
@router.post("/credits")
async def create_credit(credit_data: CreditRequest, db: firestore.client = Depends(get_db), token: str = Security(oauth2_scheme)):
    try:
        await update_credit(token=token, amount=credit_data.amount, type=CreditTypeEnum.topUp, db=db)
        
        return {"message": "Credit added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# list credits api
@router.get("/credits", response_model=List[CreditResponse])
async def list_credits(order_by: str = Query("created_at"), limit: int = Query(20), db: firestore.client = Depends(get_db), token: str = Security(oauth2_scheme)):
    try:
        # user info
        userFromToken = await validate_firebase_token(token)
        user_id = userFromToken.get("uid")

        # fetch all documents
        credits_ref = db.collection("credits").where("user_id", "==", user_id).order_by(order_by).limit(limit).stream()
        
        # parse documents
        credits_data = []
        for doc in credits_ref:
            credit_data = doc.to_dict()
            credit_data["id"] = doc.id
            credits_data.append(CreditResponse(**credit_data))
        
        return credits_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))