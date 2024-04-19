from fastapi import FastAPI

app = FastAPI()

@app.get("/", tags=["Root"])
async def hello():
    return {"message": "Hello"}