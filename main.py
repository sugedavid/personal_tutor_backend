from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from schemas import UserRegistrationRequest, UserRegistrationResponse, MessageRequest, MessageResponse
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import auth, firestore, exceptions
from openai import OpenAI
import os

from tutors.routes import router as tutors_router

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:3000",  # Next.js app origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

# initialize Firebase Admin SDK
firebase_cred = firebase_admin.credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(firebase_cred)

db = firestore.client()

# initialize OpenAI API
openai_client = OpenAI(api_key=os.getenv("PERSONAL_TUTOR_OPENAI_API_KEY"))

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
    
# fetch threads api
@app.get("/v1/threads")
async def list_threads(order: str = Query("created_at"), limit: int = Query(20)):
    try:
        # threads = openai_client.beta.threads.list(
        #     order=order,
        #     limit=str(limit),
        # )

        doc_ref = db.collection("threads").limit(limit).order_by(order)
        doc = doc_ref.get()

        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# create message api
@app.post("/v1/messages", response_model=MessageResponse)
async def create_message(user_data: MessageRequest):
    try:
        thread_id = user_data.thread_id
        instructions = user_data.instructions if user_data.instructions else "Please address the user as {user_data.firstName}. The user is a {user_data.userType}"

        # check if thread exists, if not create a new thread
        if not user_data.thread_id:
            thread = openai_client.beta.threads.create()
            thread_id = thread.id

            # save threadId to firestore
            doc_ref = db.collection("threads").document(thread_id)
            doc_ref.set({"thread_id": thread_id, "assistant_id": user_data.assistant_id, "user_id": user_data.user_id, "created_at": thread.created_at})

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
            thread_id=thread.id
        )

        message_data = [message.model_dump() for message in messages.data]

        return MessageResponse(object=messages.object, data=message_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# fetch messages api
@app.get("/v1/messages", response_model=MessageResponse)
async def list_messages(thread_id: str):
    try:
        messages = openai_client.beta.threads.messages.list(
            thread_id=thread_id
        )

        # convert message instances to dictionaries
        message_data = [message.model_dump() for message in messages.data]

        return MessageResponse(object=messages.object, data=message_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))