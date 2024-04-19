
import os

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from firebase_admin import auth, exceptions, firestore
from openai import OpenAI

from schemas.user_schema import UserRegistrationRequest, UserResponse
from utils import validate_firebase_token

router = APIRouter()
openai_client = OpenAI(api_key=os.getenv("PERSONAL_TUTOR_OPENAI_API_KEY"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    return firestore.client()

# register user api
@router.post("/users", response_model=UserResponse)
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
                "user_id": user.uid,
                "first_name":user_data.first_name,
                "last_name":user_data.last_name,
                "display_name": user.display_name,
                "email": user_data.email,
                "credits": 5,
                "currency":"£"
            }
        )

        return UserResponse(
                user_id=user.uid, 
                first_name=user_data.first_name, 
                last_name=user_data.last_name, 
                display_name=user.display_name, 
                email=user.email,
                credits=5,
                currency="£"
            )
    
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# user api
@router.get("/users", response_model=UserResponse)
async def get_user(db: firestore.client = Depends(get_db), token: str = Security(oauth2_scheme)):
    try:

        # user info
        userFromToken = await validate_firebase_token(token)
        user_id = userFromToken.get("uid")

        # fetch all documents
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        # check if the user document exists
        if user_doc.exists:
            # extract user data from the document
            user_data = user_doc.to_dict()
            return UserResponse(**user_data)
        else:
            # user document does not exist
            return None

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))