from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..schemas.usuario import UsuarioCreate
from ..services.usuario_service import criar_usuario

router = APIRouter()

@router.post("/usuarios")
def criar(user: UsuarioCreate, db: Session = Depends(get_db)):
    return criar_usuario(db, user.nome, user.email, user.senha)