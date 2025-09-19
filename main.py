from fastapi import FastAPI, Request,HTTPException, Depends, Header
from typing import List,Annotated, Optional
import auth
from supabase_client import get_supabase
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Annotated
from pydantic import BaseModel #used for data validation and useful error messages
from auth import get_current_user
import datetime
from services.reddit import create_comment

app = FastAPI()
app.include_router(auth.router)

user_dependency = Annotated[dict, Depends(get_current_user)]

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
async def dashboard_page(request: Request):
    # company_name = db.query()
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/dashboard-data")
async def get_dashboard_data(current_user: user_dependency):
    sb = get_supabase()
    res = sb.table('customers').select('id,company_name,total_searches,total_replies_posted').eq('id', current_user['id']).limit(1).execute()
    if not res.data:
        return {"error": "Customer not found"}
    customer = res.data[0]
    return {
        "id": customer['id'],
        "username": current_user["username"],
        "company_name": customer.get('company_name'),
        "search_count": customer.get('total_searches') or 0,
        "reply_count": customer.get('total_replies_posted') or 0,
    }

   

class SearchCreate(BaseModel):
    platform: str
    product_name: str
    keywords: str
    link: str
    is_active: bool

@app.post("/api/new_query")
def create_search(search: SearchCreate, current_user: Annotated[dict, Depends(get_current_user)]):
    # Whenever we include user_dependency, it will check for authorization token so in js (or where we call this API) 
    # we need to send the token in the header like this
    # headers: {
    #            "Authorization": `Bearer ${token}`,
    #            "Content-Type": "application/json"
    #          },
    sb = get_supabase()
    ins = sb.table('products').insert({
        'customer_id': current_user['id'],
        'product_name': search.product_name,
        'product_desc': search.keywords,
        'product_link': search.link,
        'created_at': datetime.datetime.utcnow().isoformat(),
        'is_active': search.is_active,
        'platform': search.platform,
    }).execute()
    if not ins.data:
        raise HTTPException(status_code=500, detail='Failed to create query')
    product_id = ins.data[0]['id']
    create_comment(product_id, current_user)
    
    return {
        "message": "Search query saved successfully",
        "data": search.dict(),
        "query_id": product_id
    }

@app.get("/api/get_queries")
def get_queries(current_user: user_dependency):
    sb = get_supabase()
    res = sb.table('products').select('id,product_name,product_desc,product_link,is_active,created_at,platform').eq('customer_id', current_user['id']).order('created_at', desc=True).execute()
    queries = res.data or []
    return {
        "queries": [
            {
                "id": q['id'],
                "product_name": q['product_name'],
                "product_desc": q['product_desc'],
                "product_link": q['product_link'],
                "is_active": q['is_active'],
                "created_at": q['created_at'],
                "platform": q['platform'],
            } for q in queries
        ]
    }
@app.get("/api/get_replies")
def get_replies(current_user: user_dependency, limit: int = 5):
    sb = get_supabase()
    res = sb.table('comments').select('id,platform,post_content,reply_text,posted_at')\
        .eq('customer_id', current_user['id']).order('posted_at', desc=True).limit(limit).execute()
    replies = res.data or []
    return {
        "replies": [
            {
                "id": r['id'],
                "platform": r.get('platform') or 'Reddit',
                "post_preview": r.get('post_content') or '',
                "reply_preview": r.get('reply_text') or '',
                "status": "Posted",
                "date": datetime.datetime.fromisoformat(r['posted_at'].replace('Z','')).strftime("%Y-%m-%d %H:%M") if r.get('posted_at') else "",
            }
            for r in replies
        ]
    }