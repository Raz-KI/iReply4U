from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter,Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Customer
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = '21308uh0412o48h1204912h9r0hfr30f19r'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/login')

# Pydantic Model for auto validation
class CreateUserRequest(BaseModel):
    email: str
    password: str
    company_name: str

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# The request at /auth will come here and the json will be automatically converted to CreateUserRequest
# This is the pydantic model which is useful for catching errors meaningfully
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest,
                       db: db_dependency):
    create_user_model = Customer(
        email=create_user_request.email,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        company_name=create_user_request.company_name
    )

    db.add(create_user_model)
    db.commit()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username,form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(user.email, user.id, timedelta(minutes=200),user.company_name)

    return {'access_token': token, "token_type": "bearer"}

def authenticate_user(email:str, password:str, db):
    user = db.query(Customer).filter(Customer.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return user

def create_access_token(email:str,user_id:int,expires_delta:timedelta,company_name:str):
    encode = {'sub': email, 'id': user_id, 'com_name': company_name}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated [str, Depends (oauth2_bearer)]): 
    try:
        payload= jwt.decode (token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        company_name: str = payload.get('com_name')
        if username is None or user_id is None:
            raise HTTPException (status_code=status. HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        return {'username': username, 'id': user_id, 'company_name': company_name}
    except JWTError:
        raise HTTPException (status_code=status. HTTP_401_UNAUTHORIZED, detail='Could not validate user.')