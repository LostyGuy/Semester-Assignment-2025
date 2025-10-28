from fastapi import FastAPI, Request, Depends, Cookie
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
    log.info("-" * 20)

def current_time() -> TIMESTAMP:
    CrT : TIMESTAMP = dt.datetime.now(dt.timezone.utc)
    return  CrT

def token_time() -> TIMESTAMP:
    TkT : TIMESTAMP = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=60)
    return  TkT

# TODO: \/ for each endpoint if user is loged in -> preventing going on endpoints without authorization 
def token_validation(session, user_ID) -> bool:
    token: str = ...
    try:
        if session:
            if token == session:
                raise NotImplementedError
        else:
            raise NotImplementedError
    except Exception as e:
        log_info("Validation Error: ", e)
        raise Exception
        
app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "templates")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates/html"))

@app.get("/", response_class=HTMLResponse, name="index")
async def main_page(request: Request, session: str = Cookie(default=None, alias="session")):
    
    #! ...
    
    return templates.TemplateResponse("index.html", {"request" : request, "session": session})

@app.get("/register", response_class=HTMLResponse, name="register")
async def register_page(request: Request, session: str = Cookie(default=None, alias="session")):

    return templates.TemplateResponse("register.html", {"request" : request, "session": session})

@app.post("/register_request", response_class=HTMLResponse)
async def register_request(request: Request, db: Session = Depends(database.get_db)):
    
    hash_salt: str = (db.query(models.secret.SECRET_SALT_KEY).filter(models.secret.ID == 1).first())[0]
    
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

@app.get("/login", response_class=HTMLResponse, name="login")
async def login_page(request: Request, session: str = Cookie(default=None, alias="session")):
    
    return templates.TemplateResponse("login.html", {"request" : request, "session": session})

# * Quality of Life Feature [QoLF]
# TODO: \/ Dynamic cookie expire? """ By default 60 minutes but don't log out if user is still active -> extend cookie expire time """
@app.post("/login_request", response_class=HTMLResponse)
async def login_request(request: Request, db: Session = Depends(database.get_db)):
    
    hash_salt: str = (db.query(models.secret.SECRET_SALT_KEY).filter(models.secret.ID == 1).first())[0]
    log_info(hash_salt)
    
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
        
    login, hashed_password = get_data(login_data=login_data)
    login_attempt_result, get_user_ID = login_attempt(login = login, hashed_password = hashed_password)
    
    CrT: TIMESTAMP = current_time()
    TkT: TIMESTAMP = token_time()
    
    if login_attempt_result:
        session_cookie = models.session(
            user_ID = get_user_ID,
            hash_user_ID = hashlib.sha256(
                str(get_user_ID).encode()
            ).hexdigest(),
            time_stamp = CrT,
            token_expires = TkT,
        )
        try:
            db.add(session_cookie)
            db.commit()
            log_info("Session created for", get_user_ID, session_cookie)
        except Exception as e:
            log_info("Session Error: ", e)
            db.rollback()
        
        response = RedirectResponse(app.url_path_for("login"), status_code= 303)
        try:
            response.set_cookie(
                key="session", 
                value=str(
                    db.query(models.session.hash_user_ID).filter(
                        models.session.user_ID == get_user_ID,
                        models.session.time_stamp == CrT,
                        ).first()
                ),
                expires=(
                    db.query(models.session.token_expires).filter(
                        models.session.user_ID == get_user_ID,
                        models.session.token_expires == TkT,
                        ).first()
                ), 
                httponly=True
            )
        except Exception as e:
            log_info("Cookie Error: ", e)
            response.headers["cookie_setting_error"] = "True"
            return response
        
        return response
    else:
        log_info("LoginError: ",login_attempt_result)

# TODO: \/ 
@app.post("/logout_request", response_class=HTMLResponse)
async def logout_request(request: Request, db: Session = Depends(database.get_db)):
    
    return RedirectResponse(url=app.url_path_for("index"), status_code=303)

# TODO: \/ 
@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, db: Session = Depends(database.get_db), session: str = Cookie(default=None, alias="session")):
    raise NotImplementedError
    return templates.TemplateResponse("profile.html", {"request" : request, "session": session})

# TODO: \/ 
@app.get("/profile/add_project", response_class=HTMLResponse)
async def add_project(request: Request, db: Session = Depends(database.get_db), session: str = Cookie(default=None, alias="session")):
    raise NotImplementedError
    return templates.TemplateResponse("profile.html", {"request" : request, "session": session})

# TODO: \/ 
@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, session: str = Cookie(default=None, alias="session")):
    raise NotImplementedError
    return templates.TemplateResponse("search.html", {"request" : request, "session": session})
