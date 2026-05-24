from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from ..dependencies import get_db
from ..schemas.usuario import UsuarioCreate, UsuarioLogin, UsuarioUpdate, UsuarioResponse
from ..services.usuario import criar_usuario, buscar_usuario, buscar_usuario_por_email, atualizar_usuario, deletar_usuario, _verificar_senha

router = APIRouter()

@router.post("/usuarios", response_model=UsuarioResponse, status_code=201)
def criar(user: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        return criar_usuario(db, user.nome, user.email, user.senha, user.data_nascimento, user.curso, user.instituicao)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email já cadastrado")

@router.post("/usuarios/login", response_model=UsuarioResponse)
def login(credenciais: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = buscar_usuario_por_email(db, credenciais.email)
    if not usuario or not _verificar_senha(credenciais.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    return usuario

@router.get("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def buscar(usuario_id: UUID, db: Session = Depends(get_db)):
    usuario = buscar_usuario(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@router.put("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def atualizar(usuario_id: UUID, dados: UsuarioUpdate, db: Session = Depends(get_db)):
    usuario = atualizar_usuario(db, usuario_id, **dados.model_dump(exclude_none=True))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@router.delete("/usuarios/{usuario_id}", status_code=204)
def deletar(usuario_id: UUID, db: Session = Depends(get_db)):
    sucesso = deletar_usuario(db, usuario_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
