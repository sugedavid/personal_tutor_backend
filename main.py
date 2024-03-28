import os

import firebase_admin
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import auth, exceptions, firestore
from openai import OpenAI

from routes.messages_route import router as messages_router
from routes.modules_route import router as modules_router
from routes.tutors_route import router as tutors_router
from schemas import UserRegistrationRequest, UserRegistrationResponse

# initialize FastAPI
app = FastAPI()

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# initialize Firebase Admin SDK
firebase_cred = firebase_admin.credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(firebase_cred)

# initialize firestore db
db = firestore.client()

# initialize OpenAI API
openai_client = OpenAI(api_key=os.getenv("PERSONAL_TUTOR_OPENAI_API_KEY"))

# routes config
app.include_router(messages_router, prefix="/v1")
app.include_router(modules_router, prefix="/v1")
app.include_router(tutors_router, prefix="/v1")

# register user api
@app.post("/v1/register", response_model=UserRegistrationResponse)
async def register_user(user_data: UserRegistrationRequest):
    try:
        # create user with provided email and password
        user = auth.create_user(
            email=user_data.email,
            password=user_data.password
        )

        # save user data to firestore
        doc_ref = db.collection("users").document(user.uid)
        doc_ref.set({"uid": user.uid, "email": user_data.email, "type": user_data.type})

        return UserRegistrationResponse(user_id=user.uid)
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=str(e))