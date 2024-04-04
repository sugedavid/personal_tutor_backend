
import os

from fastapi import APIRouter, Depends, HTTPException
from firebase_admin import auth, exceptions, firestore
from openai import OpenAI

from schemas.registration_schema import (UserRegistrationRequest,
                                         UserRegistrationResponse)

router = APIRouter()
openai_client = OpenAI(api_key=os.getenv("PERSONAL_TUTOR_OPENAI_API_KEY"))

def get_db():
    return firestore.client()

# register user api
@router.post("/register", response_model=UserRegistrationResponse)
async def register_user(user_data: UserRegistrationRequest, db: firestore.client = Depends(get_db)):
    try:
        # create user with provided email and password
        user = auth.create_user(
            display_name=f"{user_data.first_name} {user_data.last_name}",
            email=user_data.email,
            password=user_data.password
        )

        # save user data to firestore
        doc_ref = db.collection("users").document(user.uid)
        doc_ref.set(
            {
                "uid": user.uid,
                "first_name":user_data.first_name,
                "last_name":user_data.last_name,
                "display_name": user.display_name,
                "email": user_data.email,
                "credits": 5,
                "currency":"£"
            }
        )

        return UserRegistrationResponse(user_id=user.uid, first_name=user_data.first_name, last_name=user_data.last_name, display_name=user.display_name, email=user.email)
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=str(e))