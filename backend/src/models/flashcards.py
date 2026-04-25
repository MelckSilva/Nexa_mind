from sqlalchemy import Text, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from .base import Base
from .enums import dificuldade_enum

class Flashcard(Base):
    __tablename__ = "flashcards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    material_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("materiais.id", ondelete="CASCADE")
    )

    pergunta: Mapped[str] = mapped_column(Text, nullable=False)
    resposta: Mapped[str] = mapped_column(Text, nullable=False)

    nivel_dificuldade = mapped_column(dificuldade_enum, default="medio")

    acertos: Mapped[int] = mapped_column(Integer, default=0)
    erros: Mapped[int] = mapped_column(Integer, default=0)

    ultima_revisao: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    proxima_revisao: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    gerado_em: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    material = relationship("Material", back_populates="flashcards")