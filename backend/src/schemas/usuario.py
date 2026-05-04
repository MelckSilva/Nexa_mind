from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from pydantic.config import ConfigDict
from uuid import UUID
class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=150)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    data_nascimento: Optional[date] = None
    curso: Optional[str] = Field(None, max_length=100)
    instituicao: Optional[str] = Field(None, max_length=150)

    model_config = ConfigDict(extra="forbid")

class UsuarioResponse(BaseModel):
    id: UUID
    nome: str
    email: EmailStr
    data_nascimento: Optional[date] = None
    curso: Optional[str] = None
    instituicao: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)