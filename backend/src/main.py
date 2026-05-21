from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routes import usuario, disciplina, material, flashcard, chat, resumo

app = FastAPI(
    title="NexaMind API",
    description="API da plataforma inteligente de estudos NexaMind",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def home():
    return {"msg": "NexaMind API rodando"}


app.include_router(usuario.router)
app.include_router(disciplina.router)
app.include_router(material.router)
app.include_router(flashcard.router)
app.include_router(chat.router)
app.include_router(resumo.router)