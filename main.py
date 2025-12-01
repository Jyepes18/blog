from pymongo import MongoClient
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException, Cookie
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.hash import pbkdf2_sha256
from pathlib import Path
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Union
from dotenv import load_dotenv
import os
from bson import ObjectId

# Cargar variables de entorno
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
TOKEN_SECONDS_EXPIRATE = int(os.getenv("TOKEN_SECONDS_EXPIRATE"))


# Inicializar la aplicación FastAPI
app = FastAPI()

# Montar directorios estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuración de templates
templates = Jinja2Templates(directory="templates")

# Conexión a la base de datos MongoDB
client = MongoClient('localhost', 27017)
db = client['blog']
print("Conexión exitosa a MongoDB")
print(client.list_database_names())

## Funciones de utilidad
def get_user(email: str, usuarios_collection):
    user_data = usuarios_collection.find_one({"email": email})
    return user_data

def authenticate(password_hash: str, password_plain: str):
    is_valid = pbkdf2_sha256.verify(password_plain, password_hash)
    return is_valid

def create_token(data: dict):
    data_token = data.copy()
    data_token["exp"] = datetime.utcnow() + timedelta(seconds=TOKEN_SECONDS_EXPIRATE)
    token_jwt = jwt.encode(data_token, key=SECRET_KEY, algorithm="HS256")
    return token_jwt

# Rutas de la aplicación

# Página de inicio (login)
@app.get("/", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Página de registro
@app.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Enviar datos del registro
@app.post("/submit_register", response_class=HTMLResponse)
async def send_dates(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...), 
                     img: UploadFile = File(...)):
    coleccion = db['usuarios']
    img_path = Path("static/images")
    img_path.mkdir(parents=True, exist_ok=True) 
    img_filename = img.filename
    img_file_path = img_path / img_filename
    with open(img_file_path, "wb") as buffer:
        buffer.write(await img.read())
    
    hashed_password = pbkdf2_sha256.hash(password)
    usuario = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "img_filename": img_filename  
    }

    coleccion.insert_one(usuario)
    return templates.TemplateResponse("succes.html", {"request": request})

# Autenticación y creación de token
@app.post("/users/login", response_class=HTMLResponse)
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    usuarios_collection = db['usuarios']
    user_data = get_user(email, usuarios_collection)
    if user_data is None:
        return RedirectResponse("/notLogin", status_code=302)

    is_authenticated = authenticate(user_data["password"], password)
    if not is_authenticated:
        return RedirectResponse("/notLogin", status_code=302)

    token = create_token({"email": user_data['email']})
    return RedirectResponse(
        "/users/index",
        status_code=302,
        headers={
            "Set-Cookie": f"access_token={token}; Max-Age={TOKEN_SECONDS_EXPIRATE}"
        }
    )

# Página de inicio de usuario
@app.get("/users/index", response_class=HTMLResponse)
async def index(request: Request, access_token: Union[str, None] = Cookie(None)):
    if access_token is None:
        return RedirectResponse("/", status_code=302)
    
    try:
        data_user = jwt.decode(access_token, key=SECRET_KEY, algorithms=["HS256"])
        usuarios_collection = db['usuarios']
        user_data = get_user(data_user["email"], usuarios_collection)
        if user_data is None:
            return RedirectResponse("/", status_code=302)
    except JWTError:
        return RedirectResponse("/", status_code=302)
    
    posts_collection = db["post"]
    posts = list(posts_collection.find())  

    for post in posts:
        user = usuarios_collection.find_one({"email": post["user_id"]})
        if user:
            post["user_name"] = user.get("name", "Desconocido")
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "user": user_data, 
        "posts": posts
    })

# Cerrar sesión
@app.post("/users/logout")
async def logout(request: Request):
    try:
        return RedirectResponse("/", status_code=302, headers={"Set-Cookie": "access_token=: Max-Age=0"})
    except HTMLResponse:
        return templates.TemplateResponse("error.html", {"request": request})

# Crear nuevo post
@app.get("/users/post", response_class=HTMLResponse)
async def get_post(request: Request):
    return templates.TemplateResponse("create.html", {"request" : request})

@app.post("/users/post")
async def create_post(request: Request, 
                      title: str = Form(...), 
                      description: str = Form(...), 
                      access_token: Union[str, None] = Cookie(None)):
    if access_token is None:
        return RedirectResponse("/", status_code=302)
    
    try:
        data_user = jwt.decode(access_token, key=SECRET_KEY, algorithms=["HS256"])
        user_id = data_user["email"] 
    except JWTError:
        return RedirectResponse("/", status_code=302)
    
    coleccion = db["post"]
    post = {
        "user_id": user_id,
        "title": title,
        "description": description,
        "created_at": datetime.utcnow().strftime("%Y-%m-%d")
    }

    result = coleccion.insert_one(post)

    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Error al crear el post")

    return RedirectResponse("/users/index", status_code=302)

# Perfil de usuario
@app.get("/users/porfol", response_class=HTMLResponse)
async def get_porfol(request: Request, access_token: Union[str, None] = Cookie(None)):
    if access_token is None:
        return RedirectResponse("/", status_code=302)
    
    try:
        data_user = jwt.decode(access_token, key=SECRET_KEY, algorithms=["HS256"])
        usuarios_collection = db["usuarios"]
        user_data = get_user(data_user["email"], usuarios_collection)
        if user_data is None:
            return RedirectResponse("/", status_code=302)
    except JWTError:
        return RedirectResponse("/", status_code=302)
    
    post_collection = db["post"]
    posts = list(post_collection.find({"user_id": data_user["email"]}))
    
    return templates.TemplateResponse("perfil.html", {"request" : request, "user" : user_data, "posts" : posts})

# Error de no autenticación
@app.get("/notLogin", response_class=HTMLResponse)
async def not_login_succes(request: Request):
    return templates.TemplateResponse("notLogin.html", {"request" : request})

# Eliminar post
@app.post("/users/delete_post/{post_id}")
async def delete_post(post_id: str, request : Request, access_token: Union[str, None] = Cookie(None)):
    posts_collection = db["post"]
    if access_token is None:
        return RedirectResponse("/", status_code=302)
    
    try:
        data_user = jwt.decode(access_token, key=SECRET_KEY, algorithms=["HS256"])
        usuarios_collection = db["usuarios"]
        user_data = get_user(data_user["email"], usuarios_collection)
        if user_data is None:
            return RedirectResponse("/", status_code=302)
    except JWTError:
        return RedirectResponse("/", status_code=302)
    
    if not ObjectId.is_valid(post_id):
        return templates.TemplateResponse("error.html", {"request": request})
    
    post = posts_collection.find_one({"_id": ObjectId(post_id)})
    if not post:
        return templates.TemplateResponse("error.html", {"request": request})
    
    delete_result = posts_collection.delete_one({"_id": ObjectId(post_id)})
    if delete_result.deleted_count == 0:
        return templates.TemplateResponse("error.html", {"request": request})
    
    return RedirectResponse("/users/porfol", status_code=302)

# Actualizar post
@app.post("/users/update_post/{post_id}")
async def update_post(post_id: str, request: Request, 
                      title: str = Form(...), 
                      description: str = Form(...), 
                      access_token: Union[str, None] = Cookie(None)):
    if access_token is None:
        return RedirectResponse("/", status_code=302)
    
    try:
        data_user = jwt.decode(access_token, key=SECRET_KEY, algorithms=["HS256"])
        user_id = data_user["email"]
    except JWTError:
        return RedirectResponse("/", status_code=302)
    
    post_collection = db["post"]
    result = post_collection.update_one(
        {"_id": ObjectId(post_id), "user_id": user_id},
        {"$set": {"title": title, "description": description, "updated_at": datetime.utcnow().strftime("%Y-%m-%d")}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Post no encontrado o no se modificó")
    
    return RedirectResponse("/users/porfol", status_code=302)
