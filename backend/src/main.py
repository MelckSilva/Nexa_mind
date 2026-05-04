from fastapi import FastAPI
from .routes import usuario

app = FastAPI()

@app.get("/")
def home():
    return {"msg": "NexaMind API rodando"}

app.include_router(usuario.router)