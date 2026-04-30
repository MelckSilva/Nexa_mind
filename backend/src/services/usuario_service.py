from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ..models.user import Usuario

pwd = CryptContext(schemes=["bcrypt"])

def criar_usuario(db: Session, nome: str, email: str, senha: str):
    senha_hash = pwd.hash(senha)

    usuario = Usuario(
        nome=nome,
        email=email,
        senha_hash=senha_hash
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario