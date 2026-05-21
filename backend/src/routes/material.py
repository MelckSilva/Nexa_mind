import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from uuid import UUID

from ..dependencies import get_db
from ..schemas.material import MaterialCreate, MaterialResponse
from ..services.material import (
    criar_material,
    listar_materiais,
    buscar_material,
    marcar_como_processado,
    deletar_material,
)

from ai.pipelines.rag_chat import indexar_material_pipeline

router = APIRouter()

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
TIPOS_SUPORTADOS = {"pdf", "docx", "txt", "md"}


def obter_tipo_arquivo(nome_arquivo: str) -> str:
    extensao = Path(nome_arquivo).suffix.lower().replace(".", "")

    if extensao not in TIPOS_SUPORTADOS:
        raise HTTPException(
            status_code=400,
            detail="Tipo de arquivo não suportado. Envie PDF, DOCX, TXT ou MD.",
        )

    return extensao


@router.post("/materiais", response_model=MaterialResponse, status_code=201)
def criar(disciplina_id: UUID, material: MaterialCreate, db: Session = Depends(get_db)):
    return criar_material(
        db,
        disciplina_id,
        material.titulo,
        material.tipo_arquivo,
        material.caminho_arquivo,
        material.tamanho_bytes,
        material.paginas,
        material.idioma,
    )


@router.post("/materiais/upload", response_model=MaterialResponse, status_code=201)
def upload_material(
    disciplina_id: UUID,
    arquivo: UploadFile = File(...),
    titulo: str | None = Form(None),
    idioma: str = Form("pt"),
    db: Session = Depends(get_db),
):
    tipo_arquivo = obter_tipo_arquivo(arquivo.filename or "")

    pasta_destino = UPLOAD_DIR / str(disciplina_id)
    pasta_destino.mkdir(parents=True, exist_ok=True)

    nome_seguro = Path(arquivo.filename or "material").name
    nome_final = f"{uuid.uuid4()}_{nome_seguro}"
    caminho_arquivo = pasta_destino / nome_final

    with caminho_arquivo.open("wb") as buffer:
        shutil.copyfileobj(arquivo.file, buffer)

    material = criar_material(
        db=db,
        disciplina_id=disciplina_id,
        titulo=titulo or Path(nome_seguro).stem,
        tipo_arquivo=tipo_arquivo,
        caminho_arquivo=str(caminho_arquivo),
        tamanho_bytes=caminho_arquivo.stat().st_size,
        paginas=None,
        idioma=idioma,
    )

    try:
        indexar_material_pipeline(
            material_id=str(material.id),
            disciplina_id=str(material.disciplina_id),
            titulo=material.titulo,
            caminho_arquivo=material.caminho_arquivo,
            tipo_arquivo=material.tipo_arquivo,
        )
    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=f"Material salvo, mas houve erro ao processar com IA: {erro}",
        )

    material_processado = marcar_como_processado(db, material.id)
    return material_processado


@router.get("/materiais", response_model=list[MaterialResponse])
def listar(disciplina_id: UUID, db: Session = Depends(get_db)):
    return listar_materiais(db, disciplina_id)


@router.get("/materiais/{material_id}", response_model=MaterialResponse)
def buscar(material_id: UUID, db: Session = Depends(get_db)):
    material = buscar_material(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    return material


@router.patch("/materiais/{material_id}/processado", response_model=MaterialResponse)
def processar(material_id: UUID, db: Session = Depends(get_db)):
    material = marcar_como_processado(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    return material


@router.delete("/materiais/{material_id}", status_code=204)
def deletar(material_id: UUID, db: Session = Depends(get_db)):
    sucesso = deletar_material(db, material_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Material não encontrado")