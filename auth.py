from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, SQLModel, select

from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from db import engine
from models import User, UserCreate, UserPublic

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


class Token(SQLModel):
    access_token: str
    token_type: str
    id: int
    username: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user_by_username(username: str) -> Optional[User]:
    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        return session.exec(statement).first()


def authenticate_user(username: str, password: str) -> Optional[User]:
    user = get_user_by_username(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o faltantes",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user


@auth_router.post("/register", response_model=UserPublic, status_code=201)
def register_user(user_in: UserCreate):
    if get_user_by_username(user_in.username):
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    user = User(username=user_in.username, hashed_password=get_password_hash(user_in.password))
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@auth_router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "id": user.id, "username": user.username}
