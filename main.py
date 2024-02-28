from fastapi import FastAPI, HTTPException
from schemas import UserRegistrationRequest, UserRegistrationResponse, UserLoginRequest, UserLoginResponse
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import auth, exceptions
import requests
import os

# load_dotenv()

app = FastAPI()

# FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

# Initialize Firebase Admin SDK
cred = firebase_admin.credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# register user endpoint
@app.post("/v1/register", response_model=UserRegistrationResponse)
async def register_user(user_data: UserRegistrationRequest):
    try:
        # create user with provided email and password
        user = auth.create_user(
            email=user_data.email,
            password=user_data.password
        )
        return UserRegistrationResponse(userId=user.uid)
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# # login user endpoint
# @app.post("/v1/login", response_model=UserLoginResponse)
# async def login_user(user_data: UserLoginRequest):
#     try:
#         # sign in user with provided email and password
#         user = auth.get_user_by_email(user_data.email)
#         id_token = user.get_id_token()
#         refresh_token = user.get_refresh_token()

#         return UserLoginResponse(
#             idToken=id_token,
#             refreshToken=refresh_token,
#             authTime=user.auth_time,
#             userId=user.uid,
#             emailVerified=user.email_verified
#         )
#     except auth.AuthError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except requests.exceptions.RequestException as e:
#         raise HTTPException(status_code=500, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
# @app.post("/login", response_model=UserLoginResponse)
# async def login_user(user_data: UserLoginRequest):
#     try:
#         # Authenticate user with provided email and password
#         user = auth.get_user_by_email(user_data.email)
#         if user:
#             # if user exists, attempt to sign in
#             user = auth.authenticate(email=user_data.email, password=user_data.password)
#             if user:
#                 # if authentication successful, return user UID
#                 return  UserLoginResponse(
#                     idToken=user.get_id_token(),
#                     refreshToken=user.get_refresh_token(),
#                     authTime=user.auth_time,
#                     userId=user.uid,
#                     emailVerified=user.email_verified
#                 )
#             else:
#                 # if authentication fails, raise HTTPException
#                 raise HTTPException(status_code=401, detail="Incorrect email or password")
#         else:
#             # if user does not exist, raise HTTPException
#             raise HTTPException(status_code=401, detail="User not found")
#     except exceptions.FirebaseError as e:
#         # Handle authentication errors
#         raise HTTPException(status_code=500, detail=str(e))