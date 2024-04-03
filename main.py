import os

import firebase_admin
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import firestore
from openai import OpenAI

from routes.messages_route import router as messages_router
from routes.modules_route import router as modules_router
from routes.registration_route import router as registration_router
from routes.tutors_route import router as tutors_router

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
app.include_router(registration_router, prefix="/v1")