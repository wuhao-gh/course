from datetime import datetime, timedelta, timezone
from sqlmodel import select
from typing import Annotated

import jwt
from fastapi import APIRouter, Form, Response
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import Session

from db import get_session
from model import BaseEntity, Field

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "3e0a8e8d32e27a6d896e3bceb373aec20e9e058e853a5bdf01ae3055e4206044"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseEntity):
    """用户模型"""
    name: str
    email: str = Field(unique=True, index=True)
    role: str
    status: str | None


class User(UserBase, table=True):
    """用户表"""
    password_hash: str

class UserCreate(UserBase):
    """创建用户"""
    password: str

class UserView(UserBase):
    """用户视图"""


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(prefix="/api/auth", tags=["认证授权"])

def verify_password(plain_password, password_hash):
    return pwd_context.verify(plain_password, password_hash)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str, session: Session):
    return session.exec(select(User).where(User.name == username)).first()


def authenticate_user(username: str, password: str, session: Session):
    user = get_user(username, session)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username, session=session)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.status != "激活":
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name, "role": user.role}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer", expires_in=access_token_expires.seconds)


@router.get("/user/me", response_model=UserView)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/user", response_model=list[UserView])
async def get_users(session: Session = Depends(get_session)):
    """获取所有用户"""
    users = session.exec(select(User)).all()
    return users


@router.get("/students", response_model=list[UserView])
async def get_students(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """获取所有学生列表"""
    if current_user.role != 'teacher':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can access student list"
        )
    
    statement = select(User).where(User.role == 'student')
    students = session.exec(statement).all()
    return students
