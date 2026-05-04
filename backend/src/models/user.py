from sqlalchemy import String, Text, Date, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from .base import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(Text, nullable=False)

    data_nascimento: Mapped[datetime] = mapped_column(Date, nullable=True)
    foto_perfil: Mapped[str] = mapped_column(Text, nullable=True)
    curso: Mapped[str] = mapped_column(String(200), nullable=True)
    instituicao: Mapped[str] = mapped_column(String(200), nullable=True)

    data_cadastro: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relacionamentos
   # disciplinas = relationship("Disciplina", back_populates="usuario", cascade="all, delete")
    #sessoes = relationship("SessaoChat", back_populates="usuario", cascade="all, delete")