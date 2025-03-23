from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import User, get_user_db
from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: str, expires_delta: timedelta = None):
    to_encode = {"sub": data}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(username: str, password: str):
    db = next(get_user_db())
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        return False
    return {"username": user.username}

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autorizado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        return {"username": username}
    except JWTError:
        raise credentials_exception

def register_user(username: str, password: str, question: str, answer: str):
    db = next(get_user_db())
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Usuário já existe")
    hashed_password = get_password_hash(password)
    hashed_answer = get_password_hash(answer)
    user = User(username=username, password=hashed_password,
                security_question=question, security_answer=hashed_answer)
    db.add(user)
    db.commit()
    return {"msg": "Usuário registrado com sucesso"}

class reset_password_flow:
    @staticmethod
    def get_security_question(username: str):
        db = next(get_user_db())
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return {"question": user.security_question}

    @staticmethod
    def confirm_and_update(username: str, answer: str, new_password: str):
        db = next(get_user_db())
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(answer, user.security_answer):
            raise HTTPException(status_code=403, detail="Resposta incorreta")
        user.password = get_password_hash(new_password)
        db.commit()
        return {"msg": "Senha atualizada com sucesso"}
