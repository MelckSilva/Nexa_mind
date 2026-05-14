"""
Wrapper sobre o ChromaDB.

Modelo de dados:
    - Uma única coleção global: "materiais"
    - Cada chunk vira um documento com:
        * id: f"{material_id}::chunk_{N}"
        * embedding: vetor 384-d do MiniLM
        * metadata: {material_id, disciplina_id, chunk_index, titulo}
        * document: o texto do chunk
    - Filtros por material_id ou disciplina_id usam o `where` do Chroma

Por que uma coleção só com metadados (e não uma coleção por disciplina)?
    - Simplicidade: criar/deletar coleções por disciplina obriga sincronizar
      com o Postgres, e o Chroma tem limites de quantidade de coleções.
    - Filtro por metadata é a abordagem oficial recomendada.

Persistência configurada em CHROMA_PATH (default: ai/data/chroma).
Distance: cosine (mesmo da A4 do prof).
"""

from __future__ import annotations

import chromadb
from chromadb.api.models.Collection import Collection

from ..core.config import CHROMA_PATH
from ..core.embeddings import embed_texts, embed_text

COLLECTION_NAME = "materiais"

# Singletons pro client e collection (criados na 1ª chamada)
_client: chromadb.PersistentClient | None = None
_collection: Collection | None = None


def _get_collection() -> Collection:
    """Retorna a coleção, criando se ainda não existir."""
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},  # mesmo da A4
        )
    return _collection


def index_material(
    material_id: str,
    disciplina_id: str,
    titulo: str,
    chunks: list[str],
) -> int:
    """
    Indexa os chunks de um material na coleção.

    Se o material já estiver indexado (mesmos ids), o upsert sobrescreve —
    útil pra reprocessamento.

    Returns:
        Quantidade de chunks indexados.
    """
    if not chunks:
        return 0

    collection = _get_collection()
    ids = [f"{material_id}::chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "material_id": material_id,
            "disciplina_id": disciplina_id,
            "titulo": titulo,
            "chunk_index": i,
        }
        for i in range(len(chunks))
    ]
    embeddings = embed_texts(chunks)

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    return len(chunks)


def delete_material(material_id: str) -> None:
    """Remove todos os chunks de um material (chame ao deletar material no backend)."""
    collection = _get_collection()
    collection.delete(where={"material_id": material_id})


def delete_disciplina(disciplina_id: str) -> None:
    """Remove todos os chunks de todos os materiais de uma disciplina."""
    collection = _get_collection()
    collection.delete(where={"disciplina_id": disciplina_id})


def search(
    pergunta: str,
    *,
    top_k: int,
    disciplina_id: str | None = None,
    material_id: str | None = None,
) -> list[dict]:
    """
    Busca os top-K chunks mais similares à pergunta.

    Args:
        pergunta: Texto da pergunta do usuário.
        top_k: Quantos chunks recuperar.
        disciplina_id: Se informado, restringe aos materiais dessa disciplina.
        material_id: Se informado, restringe a um único material.
                     (Tem precedência sobre disciplina_id.)

    Returns:
        Lista de dicts {texto, metadata, distancia} ordenados do mais
        similar pro menos similar.
    """
    collection = _get_collection()

    # Monta o filtro where do Chroma
    where: dict | None = None
    if material_id:
        where = {"material_id": material_id}
    elif disciplina_id:
        where = {"disciplina_id": disciplina_id}

    query_embedding = embed_text(pergunta)
    resultados = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where,
    )

    # Chroma retorna listas aninhadas (1 nível por query). Pegamos a primeira.
    docs = resultados.get("documents", [[]])[0]
    metas = resultados.get("metadatas", [[]])[0]
    dists = resultados.get("distances", [[]])[0]

    return [
        {"texto": doc, "metadata": meta, "distancia": dist}
        for doc, meta, dist in zip(docs, metas, dists)
    ]


def count_chunks(material_id: str) -> int:
    """Quantos chunks um material tem indexado (útil pra debug)."""
    collection = _get_collection()
    resultado = collection.get(where={"material_id": material_id})
    return len(resultado.get("ids", []))