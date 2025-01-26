from fastapi import APIRouter, Request, Form, Cookie, HTTPException
from fastapi.responses import RedirectResponse
from pymongo import MongoClient
from bson import ObjectId
from jose import jwt, JWTError
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter()

client = MongoClient('localhost', 27017)
db = client['blog']

@router.post("/users/post")
async def create_post(request: Request, title: str = Form(...), description: str = Form(...), access_token: str = Cookie(None)):
    if not access_token:
        return RedirectResponse("/", status_code=302)
    
    try:
        data_user = jwt.decode(access_token, key=SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        return RedirectResponse("/", status_code=302)

    post = {
        "user_id": data_user["email"],
        "title": title,
        "description": description,
        "created_at": datetime.utcnow().strftime("%Y-%m-%d")
    }
    result = db["post"].insert_one(post)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Error al crear el post")
    
    return RedirectResponse("/users/index", status_code=302)
