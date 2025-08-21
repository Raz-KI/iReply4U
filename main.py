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
import datetime
from models import Product, Customer
from services.reddit import create_comment

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
user_dependency = Annotated[models.Customer, Depends(get_current_user)]

# Serve static files if needed later
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root():
    return RedirectResponse(url="/landing")


@app.get("/landing", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request,db: db_dependency):
    # company_name = db.query()
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/dashboard-data")
async def get_dashboard_data(current_user: Annotated[dict, Depends(get_current_user)]):
    return {"username": current_user["username"], "id": current_user["id"], "company_name": current_user["company_name"]}

class SearchCreate(BaseModel):
    platform: str
    product_name: str
    keywords: str
    link: str
    is_active: bool

@app.post("/api/new_query")
def create_search(search: SearchCreate,db: db_dependency, current_user: Annotated[dict, Depends(get_current_user)]):
    # Whenever we include user_dependency, it will check for authorization token so in js (or where we call this API) 
    # we need to send the token in the header like this
    # headers: {
    #            "Authorization": `Bearer ${token}`,
    #            "Content-Type": "application/json"
    #          },
    create_new_query = Product(
        customer_id=current_user["id"],
        product_name=search.product_name,
        product_desc=search.keywords,
        product_link=search.link,
        created_at=datetime.datetime.utcnow(),
        is_active=search.is_active,
        platform=search.platform
    )
    db.add(create_new_query)
    db.commit()
    product_id = db.query(Product.id).filter(Product.product_desc == search.keywords).first()[0]
    create_comment(product_id,db)

    
    
    return {
        "message": "Search query saved successfully",
        "data": search.dict(),
        "query_id": create_new_query.id
    }

@app.get("/api/get_queries")
def get_queries(db: db_dependency, current_user: user_dependency):
    queries = db.query(Product).filter(Product.customer_id == current_user["id"]).all()
    return {
        "queries": [
            {
                "id": query.id,
                "product_desc": query.product_desc,
                "is_active": query.is_active,
                "created_at": query.created_at,
                "platform": query.platform,
            } for query in queries
        ]
    }
