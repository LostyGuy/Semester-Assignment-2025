from fastapi import FastAPI, Request, Depends, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
#! Jinja partial package
from fastapi.responses import HTMLResponse, RedirectResponse
from python import models, database
from sqlalchemy.orm import Session
from pathlib import Path
import logging as log
import hashlib
import datetime as dt
from sqlalchemy import TIMESTAMP
from jwcrypto.jwk import JWK
from jwt import JWT, jwk_from_dict
import json

jwt = JWT()

log.basicConfig(filemode="a", 
                filename= str(Path(__file__).resolve().parent.parent / "apps_log.log"),
                level="INFO",
                )

def log_info(*message) -> None:
    log.info("-" * 20)
    log.info(" ".join(str(m) for m in message))
    log.info("-" * 20)

#! Run only one time and save it somewhere safe
#! -------------------------------------------------------    
# def create_JWT_key() -> str:
#     jwk = JWK.generate(alg="RS256", kid="666", kty="RSA", use="sig", size=2048)
#     log_info("Private||Public",jwk.export_private(as_dict=True), jwk.export_public(as_dict=True))
# create_JWT_key()
#! -------------------------------------------------------  
    
def create_encoded_JWT_token(iss_endpoint: str, aud_endpoint: str, user_ID: str, nickname: str,encription_key: dict,) -> str: # Token
    encription_key: str = jwk_from_dict(encription_key)
    now = dt.datetime.now(dt.timezone.utc)
    
    payload = {
        "iss" : f"https:127.0.0.1/8000/{iss_endpoint}",
        "aud" : f"https:127.0.0.1/8000/{aud_endpoint}",
        "sub" : str(user_ID),
        "nickname" : nickname,
        "iat" : int(now.timestamp()),
        "exp" : int((now + dt.timedelta(hours=6)).timestamp()),
    }
    return jwt.encode(payload=payload, key=encription_key, alg="RS256")

def encoded_JWT_token_validation(encryption_key: dict, JWT_token: str) -> dict: # Payload
    encryption_key: str = jwk_from_dict(encryption_key)
    return jwt.decode(message=JWT_token ,key=encryption_key, algorithms=["RS256"])
    
app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "templates")), name="static")
#! partial CSS to partial HTML
templates = Jinja2Templates(directory=str(BASE_DIR / "templates/html"))

@app.get("/", response_class=HTMLResponse, name="index")
async def main_page(request: Request, session: str = Cookie(default=None, alias="session")):  
    
    #! partial HTML code injection for loged and non-loged view
    
    return templates.TemplateResponse("index.html", {"request" : request, "session": session})

@app.get("/register", response_class=HTMLResponse, name="register")
async def register_page(request: Request, session: str = Cookie(default=None, alias="session")):
    
    ...
    
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
        time_stamp = dt.datetime.now()
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
# TODO: \/ Dynamic JWT_token expire? """ By default 60 minutes but don't log out if user is still active -> extend JWT_token expire time """
@app.post("/login_request", response_class=HTMLResponse)
async def login_request(request: Request, db: Session = Depends(database.get_db)):
    
    hash_salt: str = (db.query(models.secret.SECRET_SALT_KEY).filter(models.secret.ID == 1).first())[0]
    
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
    
    #private key is stored in other table without relation. Has to be accessed alone
    
    # TODO: \/ on each action -> endpoint action, reset expiration time so token is valid for 60minutes since last endpoint action
    
    if login_attempt_result:
        response = RedirectResponse(app.url_path_for("login"), status_code= 303)
        try:
            encryption_key: dict = json.loads(db.query(models.secret.PRIVATE_JWT_KEY).filter(models.secret.ID == 1).first()[0])
            token = create_encoded_JWT_token("/login", "/loged/", get_user_ID, login, encription_key=encryption_key)
            max_age_sec: int = 6 * 3600
            response.set_cookie(
                key="session",
                value=token,
                max_age= max_age_sec,
                httponly=True,
            )
        except Exception as e:
            log_info("Cookie Error: ", e)
            response.headers["cookie_setting_error"] = "True"
            return response
        return response
    else:
        log_info("LoginError: ",login_attempt_result)

# TODO: \/ 
@app.post("/loged/logout_request", response_class=HTMLResponse)
async def logout_request(request: Request, db: Session = Depends(database.get_db)):
    
    return RedirectResponse(url=app.url_path_for("index"), status_code=303)

# TODO: \/ 
@app.get("/loged/profile", response_class=HTMLResponse)
async def profile(request: Request, db: Session = Depends(database.get_db), session: str = Cookie(default=None, alias="session")):
    raise NotImplementedError

    #! Vulnerable method
    if session == "":
        return templates.TemplateResponse("profile.html", {"request" : request, "session": session})
    else:
        return RedirectResponse(url=app.url_path_for("index"), status_code=303)

# TODO: \/ 
@app.get("/loged/profile/add_project", response_class=HTMLResponse)
async def add_project(request: Request, db: Session = Depends(database.get_db), session: str = Cookie(default=None, alias="session")):
    raise NotImplementedError

    #! Vulnerable method
    if session == "":
        return templates.TemplateResponse("profile.html", {"request" : request, "session": session})
    else:
        return RedirectResponse(url=app.url_path_for("index"), status_code=303)

# TODO: \/ 
@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, session: str = Cookie(default=None, alias="session")):
    raise NotImplementedError
    return templates.TemplateResponse("search.html", {"request" : request, "session": session})
