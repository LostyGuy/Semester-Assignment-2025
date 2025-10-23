from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from python import models, database
from sqlalchemy.orm import Session
from pathlib import Path
import logging as log
import hashlib
import time as t

log.basicConfig(filemode="a", 
                filename= str(Path(__file__).resolve().parent.parent / "apps_log.log"),
                level=log.INFO,
                )

def log_info(*message) -> None:
    log.info("-" * 20)
    log.info(message)

def current_time() -> str:
    ts = t.strftime("%Y-%m-%d %H:%M:%S", t.localtime())
    return ts

hash_salt = "ff"

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "templates")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates/html"))

@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    a = 1
    return templates.TemplateResponse("index.html", {"request" : request, "a" : a})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    
    return templates.TemplateResponse("login.html", {"request" : request})

@app.post("/login_request", response_class=HTMLResponse)
async def login_request(hash_salt, request: Request, db: Session = Depends(database.get_db)):
    
    login_data = await request.form()
    
    def get_data(login_data):
        login: str = login_data.get("email")
        hashed_password: str = hashlib.sha256((login_data.get("passwd") + hash_salt).encode()).hexdigest()
        return login, hashed_password
    
    def login_attempt(login, hashed_password):
        login_attempt = db.query(models.users.ID).filter(models.users.email == login and models.users.hashed_password == hashed_password)
        
        
    login, hashed_password = get_data(login_data=login_data)
    login_attempt(login = login, hashed_password= hashed_password)
    
    return templates.TemplateResponse("login.html", {"request" : request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):

    return templates.TemplateResponse("register.html", {"request" : request})

@app.post("/register_request", response_class=HTMLResponse)
async def register_request(hash_salt, request: Request, db: Session = Depends(database.get_db)):
    
    form_data = await request.form()
    
    form_nickname: str = form_data.get("nickname")
    form_email: str = form_data.get("email")
    form_passwd: str = form_data.get("passwd")
    
    hashed_passwd = hashlib.sha256((form_passwd + hash_salt).encode()).hexdigest()
    
    register_new_user = models.users(
        nickname = form_nickname,
        email = form_email,
        hashed_password = hashed_passwd,
        time_stamp = current_time()
    )

    try:
        db.add(register_new_user)
        db.commit()
    except Exception as e:
        db.rollback()
        log_info(e)
        register_status: bool = False
    finally:
        new_user: int = db.query(models.users.ID).filter(models.users.email == register_new_user.email)
        register_status = True if new_user else False
            

    return templates.TemplateResponse("register.html", {"request" : request, "register_status" : register_status})

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, db: Session = Depends(database.get_db)):
    logged_user_ID = ...
    
    get_projects = db.query(models.profile).filter(
        models.profile.user_ID == logged_user_ID)
    
    return templates.TemplateResponse("profile.html", {"request" : request})

@app.get("/profile/add_project", response_class=HTMLResponse)
async def profile(request: Request, db: Session = Depends(database.get_db)):
    
    return templates.TemplateResponse("profile.html", {"request" : request})

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request):

    return templates.TemplateResponse("search.html", {"request" : request})
