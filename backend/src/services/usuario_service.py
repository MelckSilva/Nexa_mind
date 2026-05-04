from sqlalchemy.orm import Session
from passlib.context import CryptContext
from ..models.user import Usuario

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def criar_usuario(
    db: Session,
    nome: str,
    email: str,
    senha: str,
    data_nascimento=None,
    curso=None,
    instituicao=None
):
    senha_hash = pwd.hash(senha)

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