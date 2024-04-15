import os
from contextlib import asynccontextmanager

import firebase_admin
import redis.asyncio as redis
import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from firebase_admin import firestore
from openai import OpenAI

from routes.credits_route import router as credits_router
from routes.messages_route import router as messages_router
from routes.modules_route import router as modules_router
from routes.registration_route import router as registration_router
from routes.tutors_route import router as tutors_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis_connection = redis.from_url("redis://localhost:6379", encoding="utf8")
    await FastAPILimiter.init(redis_connection)
    yield
    await FastAPILimiter.close()

# initialize FastAPI
app = FastAPI(lifespan=lifespan)

# config rate limiting
limit = RateLimiter(times=20, seconds=60)

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

@app.get("/", tags=["API documentation"])
async def open_docs():
    return RedirectResponse(url="/docs")

# routes config
app.include_router(registration_router, prefix="/v1", tags=["User"], dependencies=[Depends(limit)])
app.include_router(tutors_router, prefix="/v1", tags=["Tutors"], dependencies=[Depends(limit)])
app.include_router(modules_router, prefix="/v1", tags=["Modules"], dependencies=[Depends(limit)])
app.include_router(messages_router, prefix="/v1", tags=["Messages"], dependencies=[Depends(limit)])
app.include_router(credits_router, prefix="/v1", tags=["Credits"], dependencies=[Depends(limit)])

if __name__ == "__main__":
    uvicorn.run("main:app", debug=True, reload=True)