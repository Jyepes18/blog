from fastapi import APIRouter, Form, Request, HTTPException, Cookie
from fastapi.responses import RedirectResponse, HTMLResponse
from passlib.hash import pbkdf2_sha256
from jose import jwt, JWTError
from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
TOKEN_SECONDS_EXPIRATE = int(os.getenv("TOKEN_SECONDS_EXPIRATE"))

router = APIRouter()

# Conexión a la base de datos
client = MongoClient('localhost', 27017)
db = client['blog']

def get_user(email: str):
    return db['usuarios'].find_one({"email": email})

def authenticate(password_hash: str, password_plain: str):
    return pbkdf2_sha256.verify(password_plain, password_hash)

def create_token(data: dict):
    data_token = data.copy()
    data_token["exp"] = datetime.utcnow() + timedelta(seconds=TOKEN_SECONDS_EXPIRATE)
    return jwt.encode(data_token, key=SECRET_KEY, algorithm="HS256")

@router.post("/users/login", response_class=HTMLResponse)
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    user_data = get_user(email)
    if not user_data or not authenticate(user_data["password"], password):
        return RedirectResponse("/notLogin", status_code=302)
    
    token = create_token({"email": user_data['email']})
    return RedirectResponse(
        "/users/index",
        status_code=302,
        headers={"Set-Cookie": f"access_token={token}; Max-Age={TOKEN_SECONDS_EXPIRATE}"}
    )

@router.post("/users/logout")
async def logout():
    return RedirectResponse("/", status_code=302, headers={"Set-Cookie": "access_token=: Max-Age=0"})
