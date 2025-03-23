from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.auth import authenticate_user, create_access_token, get_current_user, register_user, reset_password_flow
from app.app_logic import process_question
from pydantic import BaseModel
from app.models import Base, engine
import uvicorn

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginData(BaseModel):
    username: str
    password: str

class Question(BaseModel):
    pergunta: str

class RegisterData(BaseModel):
    username: str
    password: str
    security_question: str
    security_answer: str

class ResetRequest(BaseModel):
    username: str

class ResetConfirm(BaseModel):
    username: str
    security_answer: str
    new_password: str

@app.post("/login")
def login(data: LoginData):
    user = authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = create_access_token(user["username"])
    return {"access_token": token, "token_type": "bearer"}

@app.post("/register")
def register(data: RegisterData):
    return register_user(data.username, data.password, data.security_question, data.security_answer)

@app.post("/reset-password")
def reset_password(data: ResetRequest):
    return reset_password_flow.get_security_question(data.username)

@app.post("/reset-password/confirm")
def reset_confirm(data: ResetConfirm):
    return reset_password_flow.confirm_and_update(data.username, data.security_answer, data.new_password)

@app.post("/consultar")
def consultar(pergunta: Question, user: str = Depends(get_current_user)):
    return process_question(pergunta.pergunta)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
