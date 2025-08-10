from fastapi import FastAPI, Request,HTTPException, Depends, Header
from typing import List,Annotated, Optional
import auth
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Annotated
from pydantic import BaseModel #used for data validation and useful error messages
from auth import get_current_user

app = FastAPI()
app.include_router(auth.router)
models.Base.metadata.create_all(bind=engine)

def get_db():
    db=SessionLocal()
    try:
        yield db    
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[models.Users, Depends(get_current_user)]

# Serve static files if needed later
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root():
    return RedirectResponse(url="/landing")


@app.get("/landing", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

# # Protected dashboard
# @app.get("/dashboard")
# async def dashboard_page(request: Request, user: user_dependency, db: db_dependency):
#     return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/dashboard-data")
async def get_dashboard_data(current_user: Annotated[dict, Depends(get_current_user)]):
    return {"username": current_user["username"], "id": current_user["id"]}
