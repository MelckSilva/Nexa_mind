from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class SessaoCreate(BaseModel):
    titulo: Optional[str] = Field(None, max_length=200)
    disciplina_id: Optional[UUID] = None

    model_config = ConfigDict(extra="forbid")


class SessaoTituloUpdate(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)

    model_config = ConfigDict(extra="forbid")


class MensagemCreate(BaseModel):
    conteudo: str = Field(min_length=1)

    model_config = ConfigDict(extra="forbid")


class MensagemResponse(BaseModel):
    id: UUID
    sessao_id: UUID
    papel: str
    conteudo: str
    enviado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class FonteChat(BaseModel):
    material_id: str
    titulo: str
    distancia: float | None = None


class ChatRagResponse(BaseModel):
    mensagem_usuario: MensagemResponse
    mensagem_assistente: MensagemResponse
    fontes: list[FonteChat] = []


class SessaoResponse(BaseModel):
    id: UUID
    usuario_id: UUID
    disciplina_id: Optional[UUID] = None
    titulo: Optional[str] = None
    iniciado_em: datetime

    model_config = ConfigDict(from_attributes=True)