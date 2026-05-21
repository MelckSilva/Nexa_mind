from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from ..dependencies import get_db
from ..schemas.resumo import ResumoCreate, ResumoResponse
from ..services.resumo import (
    salvar_resumo,
    buscar_resumo,
    atualizar_resumo,
    deletar_resumo,
)
from ..services.material import buscar_material

from ai.pipelines.resumo import gerar_resumo_de_arquivo

router = APIRouter()


@router.post("/resumos", response_model=ResumoResponse, status_code=201)
def criar(material_id: UUID, resumo: ResumoCreate, db: Session = Depends(get_db)):
    return salvar_resumo(db, material_id, resumo.conteudo)


@router.post("/resumos/gerar", response_model=ResumoResponse, status_code=201)
def gerar(material_id: UUID, db: Session = Depends(get_db)):
    material = buscar_material(db, material_id)

    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado")

    conteudo = gerar_resumo_de_arquivo(
        caminho_arquivo=material.caminho_arquivo,
        tipo_arquivo=material.tipo_arquivo,
        titulo=material.titulo,
    )

    resumo = atualizar_resumo(db, material_id, conteudo)
    return resumo


@router.get("/resumos/{material_id}", response_model=ResumoResponse)
def buscar(material_id: UUID, db: Session = Depends(get_db)):
    resumo = buscar_resumo(db, material_id)

    if not resumo:
        raise HTTPException(status_code=404, detail="Resumo não encontrado")

    return resumo


@router.put("/resumos/{material_id}", response_model=ResumoResponse)
def atualizar(material_id: UUID, dados: ResumoCreate, db: Session = Depends(get_db)):
    return atualizar_resumo(db, material_id, dados.conteudo)


@router.delete("/resumos/{material_id}", status_code=204)
def deletar(material_id: UUID, db: Session = Depends(get_db)):
    sucesso = deletar_resumo(db, material_id)

    if not sucesso:
        raise HTTPException(status_code=404, detail="Resumo não encontrado")