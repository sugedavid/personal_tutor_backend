import time

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from firebase_admin import auth, exceptions, firestore

from schemas.credit_schema import CreditTypeEnum


def get_db():
    return firestore.client()

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
    
# method to update user credits
async def update_credit(token: str, amount: str, type: CreditTypeEnum, db: firestore.client = Depends(get_db)):
    try:
        userFromToken = await validate_firebase_token(token)
        user_id = userFromToken.get("uid")
        # db ref
        user_ref = db.collection("users").document(user_id)
        credit_ref = db.collection("credits").document()

        current_time = int(time.time())

        # update user's credit balance
        user = user_ref.get()
        if user.exists:
            user_data = user.to_dict()
            if type == CreditTypeEnum.topUp:
                new_credits = round(user_data["credits"] + amount, 2)
            else:
                new_credits = round(user_data["credits"] - amount, 2)

                if new_credits <= 0:
                    raise ValueError("Insufficient credit balance. Top up to {type.name}")
            
            user_ref.update(
                {
                    "credits": new_credits
                }
            )
        else:
            raise HTTPException(status_code=500, detail=str("User details not found"))

        # credit history
        credit_ref.set(
            {
                "id": credit_ref.id,
                "user_id": user_id,
                "amount": amount,
                "currency": "£",
                "type": type,
                "created_at": current_time
            }
        )

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))