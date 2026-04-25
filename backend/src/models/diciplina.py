from sqlalchemy import String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from .base import Base

class Disciplina(Base):
    __tablename__ = "disciplinas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    usuario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"))

    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    semestre: Mapped[str] = mapped_column(String(20), nullable=True)
    professor: Mapped[str] = mapped_column(String(150), nullable=True)
    cor: Mapped[str] = mapped_column(String(7), nullable=True)
    descricao: Mapped[str] = mapped_column(Text, nullable=True)

    criado_em: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    atualizado_em: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="disciplinas")
    materiais = relationship("Material", back_populates="disciplina", cascade="all, delete")
    sessoes = relationship("SessaoChat", back_populates="disciplina")