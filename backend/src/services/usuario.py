from sqlalchemy.orm import Session
import bcrypt
import uuid
from ..models.user import Usuario

def _hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def _verificar_senha(senha: str, hash: str) -> bool:
    return bcrypt.checkpw(senha.encode('utf-8'), hash.encode('utf-8'))

def criar_usuario(db: Session, nome: str, email: str, senha: str, data_nascimento=None, curso=None, instituicao=None):
    senha_hash = _hash_senha(senha)
    usuario = Usuario(
        nome=nome,
        email=email,
        senha_hash=senha_hash,
        data_nascimento=data_nascimento,
        curso=curso,
        instituicao=instituicao
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

def buscar_usuario(db: Session, usuario_id: uuid.UUID):
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()

def buscar_usuario_por_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

def atualizar_usuario(db: Session, usuario_id: uuid.UUID, **dados):
    usuario = buscar_usuario(db, usuario_id)
    if not usuario:
        return None
    for campo, valor in dados.items():
        setattr(usuario, campo, valor)
    db.commit()
    db.refresh(usuario)
    return usuario

def deletar_usuario(db: Session, usuario_id: uuid.UUID):
    usuario = buscar_usuario(db, usuario_id)
    if not usuario:
        return False
    db.delete(usuario)
    db.commit()
    return True