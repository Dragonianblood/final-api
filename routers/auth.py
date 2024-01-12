from os import environ as env
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from models import Users
from database import get_db
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

JSON_SECRET = env.get("JSON_SECRET")
JSON_ALG = env.get("JSON_ALG")


class UserDBOut(BaseModel):
    name: str
    alt_name: str
    email: str


class User(BaseModel):
    id: Optional[int] = None
    name: str = Field(min_length=3)
    alt_name: str
    email: str = Field(min_length=5)
    password: str = Field(min_length=4)
    role: str
    is_active: bool = Field(default=1)
    joined_on: datetime = datetime.utcnow()

    class Config:
        json_schema_extra = {
            "example": {
                'id': 2,
                'name': 'goofball smith',
                'alt_name': '',
                'email': 'a@gmail.com',
                'password': '1234567890',
                'role': 'Admin',
                'is_active': True
            }
        }


class Token(BaseModel):
    access_token: str
    token_type: str


def authenticate(email: str, password: str, db: Session):
    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        return False
    elif not bcrypt_context.verify(password, user.password):
        return False
    return user


def create_access_token(email: str, user_id: int, expires_delta: timedelta):
    expires = datetime.now(timezone.utc) + expires_delta
    encode = {"sub": email, "id": user_id, "exp": expires}
    return jwt.encode(encode, JSON_SECRET, algorithm=JSON_ALG)


async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, JSON_SECRET, algorithms=[JSON_ALG])
        user_email: str = payload.get("sub")
        user_id: int = payload.get("id")
        if user_email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="could not find")
        return {"email": user_email, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="could not find")


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: User, db: Session = Depends(get_db)):
    new_user = Users(**user.model_dump())
    new_user.password = bcrypt_context.hash(user.password)
    db.add(new_user)
    db.commit()


@router.get("/users/me", response_model=UserDBOut)
async def get_user_profile(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user = db.query(Users).filter(Users.id == current_user.get("id")).first()

    if user is not None:
        return UserDBOut(**{"name": user.name, "alt_name": user.alt_name, "email": user.email})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user profile not found")


@router.post("/token", response_model=Token)
async def get_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email = form_data.username
    password = form_data.password
    print(form_data)

    user = authenticate(email, password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="could not varify")

    token = create_access_token(user.email, user.id, timedelta(minutes=60))
    return {"access_token": token, "token_type": "bearer"}
