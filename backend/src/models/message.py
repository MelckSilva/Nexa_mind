from sqlalchemy import Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from .base import Base
from .enums import papel_mensagem_enum

class MensagemChat(Base):
    __tablename__ = "mensagens_chat"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    sessao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sessoes_chat.id", ondelete="CASCADE")
    )

    papel = mapped_column(papel_mensagem_enum, nullable=False)
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)

    enviado_em: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    sessao = relationship("SessaoChat", back_populates="mensagens")