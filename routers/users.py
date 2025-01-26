from fastapi import APIRouter, Request, Cookie
from fastapi.responses import RedirectResponse, HTMLResponse
from jose import jwt, JWTError
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter()

client = MongoClient('localhost', 27017)
db = client['blog']

def get_user(email: str):
    return db['usuarios'].find_one({"email": email})

@router.get("/users/index", response_class=HTMLResponse)
async def index(request: Request, access_token: str = Cookie(None)):
    if not access_token:
        return RedirectResponse("/", status_code=302)
    
    try:
        data_user = jwt.decode(access_token, key=SECRET_KEY, algorithms=["HS256"])
        user_data = get_user(data_user["email"])
        if not user_data:
            return RedirectResponse("/", status_code=302)
    except JWTError:
        return RedirectResponse("/", status_code=302)

    posts = list(db["post"].find())
    return {"user": user_data, "posts": posts}
