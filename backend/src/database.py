from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL não encontrada. Configure a variável no arquivo backend/.env"
    )

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    from .models.base import Base
    from .models.enums import (
        tipo_arquivo_enum,
        dificuldade_enum,
        papel_mensagem_enum,
    )

    # Importa os models para registrar todas as tabelas no metadata do SQLAlchemy
    from .models import user, disciplina, material, resumo, flashcard, chat, message

    tipo_arquivo_enum.create(bind=engine, checkfirst=True)
    dificuldade_enum.create(bind=engine, checkfirst=True)
    papel_mensagem_enum.create(bind=engine, checkfirst=True)

    Base.metadata.create_all(bind=engine)