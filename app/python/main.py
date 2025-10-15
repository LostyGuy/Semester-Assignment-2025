from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()
templates = Jinja2Templates(directory=r"./templates/html")

@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):

    #raise Exception(NotImplementedError)

    return templates.TemplateResponse("index.html", {"request" : request})

@app.get("profile", response_class=HTMLResponse)
async def profile(request: Request):

    #raise Exception(NotImplementedError)

    return templates.TemplateResponse("profile.html", {"request" : request})

@app.get("search", response_class=HTMLResponse)
async def search(request: Request):

    #raise Exception(NotImplementedError)

    return templates.TemplateResponse("search.html", {"request" : request})