# Function to validate Firebase ID token
from fastapi import HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from firebase_admin import auth, exceptions

oauth2_scheme = OAuth2AuthorizationCodeBearer(tokenUrl="token", authorizationUrl="")

# method to validate firebase token
async def validate_firebase_token(token: str):
    try:
        # decode and verify the ID token using Firebase Admin SDK
        decoded_token = auth.verify_id_token(token)
        
        # check if user is authenticated
        if not decoded_token.get("uid"):
            raise HTTPException(status_code=401, detail="Unauthorized")

        # if token is valid, return the decoded token
        return decoded_token
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=401, detail=str(e))