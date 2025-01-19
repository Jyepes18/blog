from pymongo import MongoClient
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.hash import pbkdf2_sha256
from fastapi import UploadFile, File
from pathlib import Path


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

## Conexion BD mongo 
client = MongoClient('localhost', 27017)

db = client['blog']

print("Conexión exitosa a MongoDB")
print(client.list_database_names())
## Termina la conexion

@app.get("/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/submit", response_class=HTMLResponse)
async def send_dates(request: Request, name: str = Form(...), email: str = Form(...), password_one: str = Form(...), password_two: str = Form(...), 
                     img: UploadFile = File(...)):
    
    coleccion = db['usuarios']

    if password_one == password_two:
        
        img_path = Path("static/images")
        img_path.mkdir(parents=True, exist_ok=True) 

        img_filename = img.filename
        img_file_path = img_path / img_filename
        with open(img_file_path, "wb") as buffer:
            buffer.write(await img.read())

        hashed_password = pbkdf2_sha256.hash(password_two)

        usuario = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "img_filename": img_filename  
        }

        response = coleccion.insert_one(usuario)

        return templates.TemplateResponse("succes.html", {"request": request})
    else:
        return templates.TemplateResponse("error.html", {"request": request})


    
@app.post("/submit_login")
async def get_current_username(email: str = Form(...), password: str = Form(...)):
    coleccion = db['usuarios']
    
    usuario = coleccion.find_one({"email": email})
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    hash_password = usuario.get("password")
    
    if not pbkdf2_sha256.verify(password, hash_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    user_name = usuario.get("name")
    img_filename = usuario.get("img_filename")


    return RedirectResponse(url=f"/index?user={user_name}&img={img_filename}", status_code=303)

@app.get("/index", response_class=HTMLResponse)
async def index(request: Request, user: str = None, img: str = None):
    if user:
        user_name = user
    else:
        user_name = "Invitado"
    
    if img:
        img_filename = img
    else:
        img_filename = "default.jpg"

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user_name,
        "img_filename": img_filename
    })

@app.get("/perfil", response_class=HTMLResponse)
async def perfil(request: Request, user: str = None, img: str = None):
    if user:
        user_name = user
    else:
        user_name = "Invitado"
    
    if img:
        img_filename = img
    else:
        img_filename = "default.jpg" 

    return templates.TemplateResponse("perfil.html", {
        "request": request,
        "user": user_name,
        "img_filename": img_filename
    })
