from sqlalchemy import String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from .base import Base

class SessaoChat(Base):
    __tablename__ = "sessoes_chat"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE")
    )

    disciplina_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("disciplinas.id", ondelete="SET NULL"),
        nullable=True
    )

    titulo: Mapped[str] = mapped_column(String(200), nullable=True)
    iniciado_em: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="sessoes")
    disciplina = relationship("Disciplina", back_populates="sessoes")
    mensagens = relationship("MensagemChat", back_populates="sessao", cascade="all, delete")