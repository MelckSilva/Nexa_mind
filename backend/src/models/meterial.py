from sqlalchemy import String, Text, BigInteger, Integer, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from .base import Base
from .enums import tipo_arquivo_enum

class Material(Base):
    __tablename__ = "materiais"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    disciplina_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("disciplinas.id", ondelete="CASCADE")
    )

    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    tipo_arquivo = mapped_column(tipo_arquivo_enum, nullable=False)
    caminho_arquivo: Mapped[str] = mapped_column(Text, nullable=False)

    tamanho_bytes: Mapped[int] = mapped_column(BigInteger, nullable=True)
    paginas: Mapped[int] = mapped_column(Integer, nullable=True)
    idioma: Mapped[str] = mapped_column(String(10), default="pt")

    processado: Mapped[bool] = mapped_column(Boolean, default=False)

    data_upload: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    atualizado_em: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    disciplina = relationship("Disciplina", back_populates="materiais")
    flashcards = relationship("Flashcard", back_populates="material", cascade="all, delete")
    resumos = relationship("Resumo", back_populates="material", cascade="all, delete")