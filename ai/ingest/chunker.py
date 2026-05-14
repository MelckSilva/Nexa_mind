"""
Chunking de texto com overlap.

Evolução do split simples da A3 (sem overlap): adicionamos sobreposição
entre chunks vizinhos pra não cortar conceitos no meio.
"""

from ..core.config import CHUNK_SIZE, CHUNK_OVERLAP


def split_text(
    texto: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[str]:
    """
    Divide texto em chunks com overlap.

    Args:
        texto: Texto bruto a dividir.
        chunk_size: Tamanho máximo de cada chunk em caracteres (default: do .env).
        chunk_overlap: Quantos chars do chunk anterior se repetem no próximo.
    """
    size = chunk_size if chunk_size is not None else CHUNK_SIZE
    overlap = chunk_overlap if chunk_overlap is not None else CHUNK_OVERLAP

    if size <= 0:
        raise ValueError("chunk_size deve ser positivo")
    if overlap >= size:
        raise ValueError("chunk_overlap deve ser menor que chunk_size")

    texto = (texto or "").strip()
    if not texto:
        return []

    chunks: list[str] = []
    passo = size - overlap
    i = 0
    while i < len(texto):
        chunk = texto[i : i + size].strip()
        if chunk:
            chunks.append(chunk)
        i += passo

    return chunks