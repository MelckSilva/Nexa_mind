"""
Wrapper de embeddings usando sentence-transformers.

Modelo: all-MiniLM-L6-v2 (mesmo das aulas A3 e A4 do prof Victor).
- Dimensão: 384
- Tamanho: ~80MB (baixa automaticamente na 1ª execução)
- Multilíngue parcial (funciona razoavelmente bem em pt-BR)
- Roda em CPU sem problemas
"""

from sentence_transformers import SentenceTransformer
from .config import EMBEDDING_MODEL

# Lazy loading: o modelo pesa ~80MB e leva alguns segundos pra carregar.
# Só carrega quando alguém realmente pedir um embedding.
_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """Retorna o modelo de embeddings (carrega no 1º uso)."""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Gera embeddings para uma lista de textos.

    Retorna list[list[float]] (em vez de numpy) pra facilitar
    serialização e uso direto com ChromaDB.
    """
    if not texts:
        return []
    model = get_model()
    vectors = model.encode(texts, show_progress_bar=False)
    return vectors.tolist()


def embed_text(text: str) -> list[float]:
    """Atalho pra um único texto (ex: pergunta do usuário no RAG)."""
    return embed_texts([text])[0]


def get_dimension() -> int:
    """Dimensão dos vetores (útil pra criar coleções no vector store)."""
    return get_model().get_embedding_dimension()