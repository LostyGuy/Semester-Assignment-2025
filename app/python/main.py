from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from python import models, database
from sqlalchemy.orm import Session
from pathlib import Path
import logging as log
import hashlib
import datetime as dt
from sqlalchemy import TIMESTAMP

log.basicConfig(filemode="a", 
                filename= str(Path(__file__).resolve().parent.parent / "apps_log.log"),
                level="INFO",
                )

def log_info(*message) -> None:
    log.info("-" * 20)
    log.info(" ".join(str(m) for m in message))

def current_time() -> TIMESTAMP:
    CrT : TIMESTAMP = dt.datetime.now()
    return  CrT

def token_time() -> TIMESTAMP:
    TkT : TIMESTAMP = dt.datetime.now() + dt.timedelta(minutes=60)
    return  TkT

hash_salt = "ff"
app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "templates")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates/html"))

@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    a = 1
    return templates.TemplateResponse("index.html", {"request" : request, "a" : a})

@app.get("/login", response_class=HTMLResponse, name="login")
async def login_page(request: Request):
    
    return templates.TemplateResponse("login.html", {"request" : request})

@app.post("/login_request", response_class=HTMLResponse)
async def login_request(request: Request, db: Session = Depends(database.get_db)):
    
    def get_data(login_data) -> str:
        form_login: str = login_data.get("email")
        form_passwd: str = login_data.get("passwd")
        hashed_password: str = hashlib.sha256(
            (
                form_passwd + hash_salt
            ).encode()
        ).hexdigest()
        return form_login, hashed_password
    
    def login_attempt(login, hashed_password) -> str:
        get_user_ID: int = db.query(models.users.ID).filter(
            models.users.email == login,
            models.users.hashed_password == hashed_password,
        ).one_or_none()[0] #returns int when .first() returns tuple
        if get_user_ID:
            log_info("User exists")
            login_attempt_result: bool = True
        else:
            log_info("Log In data are wrong")
            login_attempt_result: bool = False
        
        return login_attempt_result, get_user_ID
    
    login_data = await request.form()
    log_info(login_data)
        
    login, hashed_password = get_data(login_data=login_data)
    login_attempt_result, get_user_ID = login_attempt(login = login, hashed_password= hashed_password)
    
    if login_attempt_result:
        session_cookie = models.session(
            user_ID = get_user_ID,
            time_stamp = current_time(),
            token_expires = token_time(),
        )
        try:
            db.add(session_cookie)
            db.commit()
            log_info("Session created for", get_user_ID, session_cookie)
        except Exception as e:
            log_info(e)
            db.rollback()
        
    return RedirectResponse(app.url_path_for("login"), status_code= 303)

@app.get("/register", response_class=HTMLResponse, name="register")
async def register_page(request: Request):

    return templates.TemplateResponse("register.html", {"request" : request})

@app.post("/register_request", response_class=HTMLResponse)
async def register_request(request: Request, db: Session = Depends(database.get_db)):
    
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
        new_user: int = db.query(models.users.ID).filter(
            models.users.email == register_new_user.email
        ).one_or_none()
        register_status = True if new_user else False
            

    return RedirectResponse(url=app.url_path_for("register"), status_code= 303)

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, db: Session = Depends(database.get_db)):
    logged_user_ID = ...
    
    get_projects = db.query(models.profile).filter(
        models.profile.user_ID == logged_user_ID)
    
    return templates.TemplateResponse("profile.html", {"request" : request})

@app.get("/profile/add_project", response_class=HTMLResponse)
async def add_project(request: Request, db: Session = Depends(database.get_db)):
    
    return templates.TemplateResponse("profile.html", {"request" : request})

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request):

    return templates.TemplateResponse("search.html", {"request" : request})
